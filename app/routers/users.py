from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .. import schemas, deps
from ..core.supabase_client import supabase
from ..core import security

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: dict = Depends(deps.get_current_user)):
    # Fetch roles for the current user
    user_roles_res = supabase.table("epay_user_roles").select("epay_roles(*)").eq("userId", current_user["userId"]).execute()
    roles = []
    if user_roles_res.data:
        for row in user_roles_res.data:
            if "epay_roles" in row:
                roles.append(row["epay_roles"])
    
    current_user["roles"] = roles
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_users").select("*").eq("userId", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result.data[0]
    # Fetch roles
    user_roles_res = supabase.table("epay_user_roles").select("epay_roles(*)").eq("userId", user_id).execute()
    roles = []
    if user_roles_res.data:
        for row in user_roles_res.data:
            if "epay_roles" in row:
                roles.append(row["epay_roles"])
    
    user["roles"] = roles
    return user

@router.put("/me", response_model=schemas.UserResponse)
async def update_user(
    update_data: schemas.UserUpdate,
    current_user: dict = Depends(deps.get_current_user)
):
    update_dict = {}
    if update_data.fullName is not None:
        update_dict["fullName"] = update_data.fullName
    if update_data.phoneNumber is not None:
        update_dict["phoneNumber"] = update_data.phoneNumber
    if update_data.emailId is not None:
        # Check if email is taken
        existing = supabase.table("epay_users").select("*").eq("emailId", update_data.emailId).execute()
        if existing.data and existing.data[0]["userId"] != current_user["userId"]:
            raise HTTPException(status_code=400, detail="Email already registered")
        update_dict["emailId"] = update_data.emailId
    if update_data.password is not None:
        update_dict["hashPassword"] = security.get_password_hash(update_data.password)

    if update_dict:
        result = supabase.table("epay_users").update(update_dict).eq("userId", current_user["userId"]).execute()
        return result.data[0]
    
    return current_user

@router.delete("/{user_id}", response_model=schemas.UserResponse)
async def delete_user(user_id: int, current_user: dict = Depends(deps.get_current_user)):
    # Simple active/inactive toggle
    result = supabase.table("epay_users").update({"isActive": False}).eq("userId", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]

@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_users").select("*").range(skip, skip + limit - 1).execute()
    return result.data
