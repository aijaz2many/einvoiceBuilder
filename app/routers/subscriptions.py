from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, deps
from ..core.supabase_client import supabase

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# --- Subscription Plans ---
@router.post("/plans", response_model=schemas.SubscriptionPlanResponse)
async def create_plan(plan: schemas.SubscriptionPlanBase, current_user: dict = Depends(deps.get_current_user)):
    new_plan_data = plan.model_dump()
    res = supabase.table("epay_subscription_plans").insert(new_plan_data).execute()
    return res.data[0]

@router.get("/plans", response_model=List[schemas.SubscriptionPlanResponse])
async def list_plans():
    result = supabase.table("epay_subscription_plans").select("*").eq("subscriptionPlanStatus", True).execute()
    return result.data

@router.put("/plans/{plan_id}", response_model=schemas.SubscriptionPlanResponse)
async def update_plan(
    plan_id: int, 
    plan_update: schemas.SubscriptionPlanUpdate, 
    current_user: dict = Depends(deps.get_current_user)
):
    update_data = plan_update.model_dump(exclude_unset=True)
    res = supabase.table("epay_subscription_plans").update(update_data).eq("subscriptionPlanId", plan_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return res.data[0]

# --- Subscriptions ---
@router.post("/", response_model=schemas.SubscriptionResponse)
async def create_subscription(sub: schemas.SubscriptionCreate, current_user: dict = Depends(deps.get_current_user)):
    # Verify business and plan exist
    bus = supabase.table("epay_business").select("*").eq("businessId", sub.businessId).execute()
    if not bus.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    plan = supabase.table("epay_subscription_plans").select("*").eq("subscriptionPlanId", sub.subscriptionPlanId).execute()
    if not plan.data:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    new_sub_data = sub.model_dump()
    # Convert dates to string if they are datetime objects
    if isinstance(new_sub_data.get("subscriptionStartDate"), str) is False:
        new_sub_data["subscriptionStartDate"] = new_sub_data["subscriptionStartDate"].isoformat()
    if isinstance(new_sub_data.get("subscriptionEndDate"), str) is False:
        new_sub_data["subscriptionEndDate"] = new_sub_data["subscriptionEndDate"].isoformat()

    res = supabase.table("epay_subscriptions").insert(new_sub_data).execute()
    return res.data[0]

@router.get("/", response_model=List[schemas.SubscriptionResponse])
async def list_all_subscriptions(current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_subscriptions").select("*").execute()
    return result.data

@router.get("/business/{business_id}", response_model=List[schemas.SubscriptionResponse])
async def get_business_subscriptions(business_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_subscriptions").select("*").eq("businessId", business_id).execute()
    return result.data

@router.delete("/{sub_id}")
async def delete_subscription(
    sub_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_subscriptions").delete().eq("subscriptionId", sub_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription correctly deleted"}

@router.put("/{sub_id}", response_model=schemas.SubscriptionResponse)
async def update_subscription(
    sub_id: int,
    sub_update: schemas.SubscriptionUpdate,
    current_user: dict = Depends(deps.get_current_user)
):
    update_data = sub_update.model_dump(exclude_unset=True)
    
    # Handle datetime conversion for Supabase
    if "subscriptionStartDate" in update_data and not isinstance(update_data["subscriptionStartDate"], str):
        update_data["subscriptionStartDate"] = update_data["subscriptionStartDate"].isoformat()
    if "subscriptionEndDate" in update_data and not isinstance(update_data["subscriptionEndDate"], str):
        update_data["subscriptionEndDate"] = update_data["subscriptionEndDate"].isoformat()
        
    res = supabase.table("epay_subscriptions").update(update_data).eq("subscriptionId", sub_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return res.data[0]

# Payments and Usage would follow same pattern...
