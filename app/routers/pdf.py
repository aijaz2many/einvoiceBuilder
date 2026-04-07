from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
import os
import fitz  # PyMuPDF
import httpx
from .. import schemas, deps
from ..core.supabase_client import supabase
from datetime import datetime, timezone
import io
from typing import List

router = APIRouter(prefix="/pdf", tags=["PDF"])

BUCKET_NAME = "invoice-builder"

@router.post("/upload-template/{businessId}")
async def upload_template(
    businessId: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_user)
):
    # 1. Verify business exists
    business_res = supabase.table("epay_business").select("*").eq("businessId", businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")

    file_ext = file.filename.split('.')[-1].lower()
    is_pdf = file_ext == 'pdf'
    is_image = file_ext in ['jpg', 'jpeg', 'png']

    if not is_pdf and not is_image:
        raise HTTPException(status_code=400, detail="Only PDF or Image (JPG, PNG) files are allowed")

    # 2. Upload to Supabase Storage
    try:
        file_content = await file.read()
        filename = "receipt_fields.pdf" if is_pdf else f"raw_template.{file_ext}"
        storage_path = f"{businessId}/{filename}"
        
        # Upload to Supabase
        res = supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_content,
            file_options={"upsert": "true", "content-type": file.content_type}
        )
        
        # 3. Update Business Status
        template_status = "ACTIVE" if is_pdf else "PENDING"
        supabase.table("epay_business").update({"templateStatus": template_status}).eq("businessId", businessId).execute()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

    return {
        "message": "Template uploaded successfully", 
        "status": "success",
        "templateStatus": template_status
    }

@router.get("/template/{businessId}")
async def get_template(
    businessId: int,
    current_user: dict = Depends(deps.get_current_user)
):
    # 1. Verify business exists
    business_res = supabase.table("epay_business").select("*").eq("businessId", businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business = business_res.data[0]
    if business["templateStatus"] == "MISSING":
        raise HTTPException(status_code=404, detail="No template uploaded")

    # 2. Determine file path
    filename = "receipt_fields.pdf"
    if business["templateStatus"] == "PENDING":
        # Search for raw image in storage (common files)
        filename = "raw_template.png" # Simplified for now, in real app we'd check availability
    
    try:
        # Download from Supabase
        file_res = supabase.storage.from_(BUCKET_NAME).download(f"{businessId}/{filename}")
        return Response(content=file_res, media_type="application/pdf" if ".pdf" in filename else "image/png")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Template file not found in storage")

@router.post("/save-invoice")
async def generate_invoice_pdf(
    data: schemas.InvoicePDFData, 
    current_user: dict = Depends(deps.get_current_user)
):
    # 1. Verify business and template
    business_res = supabase.table("epay_business").select("*").eq("businessId", data.businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business = business_res.data[0]
    if business.get("templateStatus") != "ACTIVE":
         raise HTTPException(status_code=400, detail="Template not active")

    # Handle Customer (Find or Create)
    customer_res = supabase.table("epay_customers").select("*").match({
        "businessId": data.businessId,
        "customerName": data.CustomerName,
        "customerPhone": data.customerPhone
    }).execute()
    
    if customer_res.data:
        customer = customer_res.data[0]
    else:
        new_customer = {
            "businessId": data.businessId,
            "customerName": data.CustomerName,
            "customerPhone": data.customerPhone,
            "customerFullAddress": data.customerFullAddress
        }
        cust_insert = supabase.table("epay_customers").insert(new_customer).execute()
        customer = cust_insert.data[0]

    # 2. PDF Generation
    try:
        # Fetch template from Supabase Storage
        template_content = supabase.storage.from_(BUCKET_NAME).download(f"{data.businessId}/receipt_fields.pdf")
        
        doc = fitz.open(stream=template_content, filetype="pdf")
        page = doc.load_page(0)
        raw_data = data.model_dump()
        
        # Custom formatting for the date in the PDF
        if "invoiceDate" in raw_data and raw_data["invoiceDate"]:
            try:
                # Try parsing standard YYYY-MM-DD format
                dt_obj = datetime.strptime(raw_data["invoiceDate"], "%Y-%m-%d")
                raw_data["invoiceDate"] = dt_obj.strftime("%d-%b-%Y")
            except ValueError:
                pass
        
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name in raw_data and raw_data[field_name] is not None:
                text_value = str(raw_data[field_name])
                rect = widget.rect
                point = (rect.x0, rect.y1 - 3)
                page.insert_text(point, text_value, fontsize=12, color=(0, 0, 0))
            page.delete_widget(widget)
        
        pdf_bytes = doc.write()
        doc.close()

        # 3. Save Invoice to Database and Storage
        safe_date = data.invoiceDate.replace("/", "-").replace("\\", "-")
        invoice_filename = f"invoice_{data.invoiceNumber}_{safe_date}.pdf"
        storage_path = f"{data.businessId}/invoices/{invoice_filename}"
        
        # Upload generated invoice
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=pdf_bytes,
            file_options={"upsert": "true", "content-type": "application/pdf"}
        )
        
        # Get Public URL
        public_url_res = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        # Handle both old and new SDK versions
        public_url = public_url_res if isinstance(public_url_res, str) else getattr(public_url_res, "public_url", str(public_url_res))

        new_invoice = {
            "businessId": data.businessId,
            "customerId": customer["customerId"],
            "invoiceNumber": data.invoiceNumber,
            "BookNo": data.BookNo,
            "invoiceAmount": data.invoiceAmount,
            "amountInWords": data.amountinwords,
            "paymentMode": data.paymentMode,
            "paymentType": data.paymentType,
            "purpose": data.purpose,
            "billCollector": data.billCollector,
            "Nazim": data.Nazim,
            "invoiceDate": data.invoiceDate,
            "pdfURL": public_url
        }
        
        try:
            supabase.table("epay_invoices").insert(new_invoice).execute()
        except Exception as db_err:
            print(f"DATABASE INSERT ERROR: {str(db_err)}")
            raise db_err

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={invoice_filename}"}
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DEBUG PDF ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/preview-invoice")
async def preview_invoice_pdf(
    data: schemas.InvoicePDFData, 
    current_user: dict = Depends(deps.get_current_user)
):
    # 1. Verify business and template
    business_res = supabase.table("epay_business").select("*").eq("businessId", data.businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business = business_res.data[0]
    if business.get("templateStatus") != "ACTIVE":
         raise HTTPException(status_code=400, detail="Template not active")

    # 2. PDF Generation
    try:
        # Fetch template from Supabase Storage
        template_content = supabase.storage.from_(BUCKET_NAME).download(f"{data.businessId}/receipt_fields.pdf")
        
        doc = fitz.open(stream=template_content, filetype="pdf")
        page = doc.load_page(0)
        raw_data = data.model_dump()
        
        # Custom formatting for the date in the PDF
        if "invoiceDate" in raw_data and raw_data["invoiceDate"]:
            try:
                # Try parsing standard YYYY-MM-DD format
                dt_obj = datetime.strptime(raw_data["invoiceDate"], "%Y-%m-%d")
                raw_data["invoiceDate"] = dt_obj.strftime("%d-%b-%Y")
            except ValueError:
                pass
        
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name in raw_data and raw_data[field_name] is not None:
                text_value = str(raw_data[field_name])
                rect = widget.rect
                point = (rect.x0, rect.y1 - 3)
                page.insert_text(point, text_value, fontsize=12, color=(0, 0, 0))
            page.delete_widget(widget)
        
        pdf_bytes = doc.write()
        doc.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=preview.pdf"}
        )
        
    except Exception as e:
        print(f"DEBUG PREVIEW ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")
