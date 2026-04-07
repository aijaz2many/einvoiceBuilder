from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .. import schemas, deps
from ..core.supabase_client import supabase
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.get("/types/", response_model=List[schemas.BusinessTypeResponse])
async def list_business_types():
    result = supabase.table("epay_business_types").select("*").eq("isActive", True).execute()
    return result.data

@router.post("/types/", response_model=schemas.BusinessTypeResponse)
async def create_business_type(
    business_type: schemas.BusinessTypeBase,
    current_user: dict = Depends(deps.get_current_user)
):
    # Check if exists
    result = supabase.table("epay_business_types").select("*").eq("businessTypeName", business_type.businessTypeName).execute()
    if result.data:
        raise HTTPException(status_code=400, detail="Business type already exists")
    
    new_type_data = business_type.model_dump()
    res = supabase.table("epay_business_types").insert(new_type_data).execute()
    return res.data[0]

@router.post("/", response_model=schemas.BusinessResponse)
async def create_business(
    business: schemas.BusinessCreate,
    current_user: dict = Depends(deps.get_current_user)
):
    # Check if business name exists
    existing = supabase.table("epay_business").select("*").eq("businessName", business.businessName).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Business name already exists")
    
    # Check if business type exists
    bt = supabase.table("epay_business_types").select("*").eq("businessTypeId", business.businessTypeId).execute()
    if not bt.data:
        raise HTTPException(status_code=400, detail="Invalid business type")
    
    new_business_data = business.model_dump()
    res = supabase.table("epay_business").insert(new_business_data).execute()
    if not res.data:
         raise HTTPException(status_code=500, detail="Failed to create business")
    
    new_business = res.data[0]

    # --- Auto-create 10-day Free Trial Subscription ---
    plan_res = supabase.table("epay_subscription_plans").select("*").eq("subscriptionPlanName", "Free Trial").execute()
    if not plan_res.data:
        plan_data = {
            "subscriptionPlanName": "Free Trial",
            "subscriptionPlanDescription": "10-day complimentary trial for new businesses",
            "subscriptionPlanPrice": 0,
            "subscriptionPlanDuration": 10,
            "subscriptionPlanStatus": True,
        }
        plan_res = supabase.table("epay_subscription_plans").insert(plan_data).execute()
    
    free_trial_plan = plan_res.data[0]

    now = datetime.now(timezone.utc)
    free_subscription = {
        "businessId": new_business["businessId"],
        "subscriptionPlanId": free_trial_plan["subscriptionPlanId"],
        "subscriptionStatus": True,
        "subscriptionStartDate": now.isoformat(),
        "subscriptionEndDate": (now + timedelta(days=10)).isoformat(),
        "autoRenew": False,
    }
    supabase.table("epay_subscriptions").insert(free_subscription).execute()

    return new_business

@router.get("/", response_model=List[schemas.BusinessResponse])
async def list_businesses(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_business").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/{business_id}", response_model=schemas.BusinessResponse)
async def get_business(business_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_business").select("*").eq("businessId", business_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Business not found")
    return result.data[0]

@router.get("/user/{user_id}", response_model=List[schemas.BusinessResponse])
async def get_user_businesses(user_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_business").select("*").eq("userId", user_id).execute()
    return result.data
