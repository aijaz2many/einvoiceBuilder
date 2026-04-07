from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import httpx
from .. import schemas, deps
from ..core.supabase_client import supabase

def format_invoice(invoice):
    if "epay_customers" in invoice and invoice["epay_customers"]:
        cust = invoice.pop("epay_customers")
        invoice["customerName"] = cust.get("customerName")
        invoice["customerPhone"] = cust.get("customerPhone")
    return invoice

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=schemas.InvoiceResponse)
async def create_invoice(
    invoice_data: schemas.InvoiceWithCustomerCreate,
    current_user: dict = Depends(deps.get_current_user)
):
    # Check if business exists
    business_res = supabase.table("epay_business").select("*").eq("businessId", invoice_data.businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # 1. Handle Customer (Find or Create)
    customer_res = supabase.table("epay_customers").select("*").match({
        "businessId": invoice_data.businessId,
        "customerName": invoice_data.customerName,
        "customerPhone": invoice_data.customerPhone
    }).execute()
    
    if customer_res.data:
        customer = customer_res.data[0]
    else:
        # Create new customer
        new_customer = {
            "businessId": invoice_data.businessId,
            "customerName": invoice_data.customerName,
            "customerPhone": invoice_data.customerPhone,
            "customerFullAddress": invoice_data.customerFullAddress
        }
        customer_insert = supabase.table("epay_customers").insert(new_customer).execute()
        customer = customer_insert.data[0]
    
    # 2. Create Invoice
    new_invoice = {
        "businessId": invoice_data.businessId,
        "customerId": customer["customerId"],
        "invoiceNumber": invoice_data.invoiceNumber,
        "invoiceAmount": invoice_data.invoiceAmount,
        "amountInWords": invoice_data.amountInWords,
        "paymentMode": invoice_data.paymentMode,
        "paymentType": invoice_data.paymentType,
        "purpose": invoice_data.purpose,
        "pdfURL": invoice_data.pdfURL
    }
    res = supabase.table("epay_invoices").insert(new_invoice).execute()
    if not res.data:
         raise HTTPException(status_code=500, detail="Failed to create invoice")
         
    return res.data[0]

@router.get("/", response_model=List[schemas.InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_invoices").select("*, epay_customers(customerName, customerPhone)").order("invoiceId", desc=True).range(skip, skip + limit - 1).execute()
    return [format_invoice(inv) for inv in result.data]

@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_invoices").select("*, epay_customers(customerName, customerPhone)").eq("invoiceId", invoice_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return format_invoice(result.data[0])

@router.get("/business/{business_id}", response_model=List[schemas.InvoiceResponse])
async def get_business_invoices(
    business_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_invoices").select("*, epay_customers(customerName, customerPhone)").eq("businessId", business_id).order("invoiceId", desc=True).execute()
    return [format_invoice(inv) for inv in result.data]

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: dict = Depends(deps.get_current_user)
):
    # Fetch invoice for pdfURL
    res = supabase.table("epay_invoices").select("*").eq("invoiceId", invoice_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice = res.data[0]
    
    # Delete from Cloud Storage first if URL exists
    if invoice.get("pdfURL"):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(invoice["pdfURL"])
        except Exception:
            pass

    supabase.table("epay_invoices").delete().eq("invoiceId", invoice_id).execute()
    return {"message": "Invoice deleted"}

@router.get("/user/{user_id}", response_model=List[schemas.InvoiceResponse])
async def get_user_invoices(
    user_id: int,
    current_user: dict = Depends(deps.get_current_user)
):
    try:
        # 1. Get all businesses owned by this user
        businesses_res = supabase.table("epay_business").select("businessId").eq("userId", user_id).execute()
        if not businesses_res.data:
            return []
        
        business_ids = [b["businessId"] for b in businesses_res.data]
        
        # 2. Get all invoices for these businesses
        result = supabase.table("epay_invoices").select("*, epay_customers(customerName, customerPhone)").in_("businessId", business_ids).order("invoiceId", desc=True).execute()
        return [format_invoice(inv) for inv in result.data]
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DEBUG USER INVOICES ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user invoices: {str(e)}")
