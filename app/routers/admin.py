from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas, deps
from ..core.supabase_client import supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_admin_stats(
    current_user: dict = Depends(deps.get_current_user)
):
    # In a real app, check if user is admin. 
    # For now, we'll assume the same logic or dependency.
    
    # Counts
    business_count = supabase.table("epay_business").select("*", count="exact").execute().count
    invoice_count = supabase.table("epay_invoices").select("*", count="exact").execute().count
    pending_templates = supabase.table("epay_business").select("*", count="exact").eq("templateStatus", "PENDING").execute().count
    missing_templates = supabase.table("epay_business").select("*", count="exact").eq("templateStatus", "MISSING").execute().count
    active_templates = supabase.table("epay_business").select("*", count="exact").eq("templateStatus", "ACTIVE").execute().count
    user_count = supabase.table("epay_users").select("*", count="exact").execute().count

    # Chart Data: Invoices over last 7 days
    # Supabase doesn't have complex group-by in current SDK as easily as SQL, 
    # but we can fetch and process or use a RPC if needed.
    # For simplicity, we'll fetch last 1000 invoices and process in Python.
    
    today = datetime.now()
    seven_days_ago = (today - timedelta(days=6)).isoformat()
    
    invoices_res = supabase.table("epay_invoices").select("createdOn").gte("createdOn", seven_days_ago).execute()
    
    invoice_chart_data = []
    for i in range(7):
        date = (today - timedelta(days=6-i)).date()
        date_str = date.strftime('%Y-%m-%d')
        # Count matching dates in invoices_res.data
        count = sum(1 for inv in invoices_res.data if inv["createdOn"][:10] == date_str)
        invoice_chart_data.append({"date": date_str, "count": count})

    return {
        "businesses": business_count,
        "invoices": invoice_count,
        "pendingTemplates": pending_templates,
        "missingTemplates": missing_templates,
        "users": user_count,
        "charts": {
            "invoiceTimeline": invoice_chart_data,
            "templateDistribution": [
                {"label": "Active", "value": active_templates},
                {"label": "Pending", "value": pending_templates},
                {"label": "Missing", "value": missing_templates}
            ]
        }
    }

@router.get("/businesses", response_model=List[schemas.BusinessResponse])
async def get_all_businesses_admin(
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_business").select("*").execute()
    return result.data
