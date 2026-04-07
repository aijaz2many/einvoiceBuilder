from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, deps
from ..core.supabase_client import supabase

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=schemas.CustomerResponse)
async def create_customer(
    customer: schemas.CustomerCreate,
    current_user: dict = Depends(deps.get_current_user)
):
    # Check if business exists
    business_res = supabase.table("epay_business").select("*").eq("businessId", customer.businessId).execute()
    if not business_res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    new_customer_data = customer.model_dump()
    res = supabase.table("epay_customers").insert(new_customer_data).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create customer")
        
    return res.data[0]

@router.get("/", response_model=List[schemas.CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_customers").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
async def get_customer(
    customer_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_customers").select("*").eq("customerId", customer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result.data[0]

@router.get("/business/{business_id}", response_model=List[schemas.CustomerResponse])
async def get_business_customers(
    business_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_customers").select("*").eq("businessId", business_id).execute()
    return result.data

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_customers").delete().eq("customerId", customer_id).execute()
    if not result.data:
         raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted"}
