from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas, deps
from ..core.supabase_client import supabase

router = APIRouter(prefix="/user-roles", tags=["User Roles"])

@router.post("/", response_model=schemas.UserRoleResponse)
async def assign_role_to_user(
    user_role: schemas.UserRoleBase, 
    current_user: dict = Depends(deps.get_current_user)
):
    # Check if user exists
    user_res = supabase.table("epay_users").select("*").eq("userId", user_role.userId).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if role exists
    role_res = supabase.table("epay_roles").select("*").eq("roleId", user_role.roleId).execute()
    if not role_res.data:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if assignment already exists
    exists = supabase.table("epay_user_roles").select("*").match({
        "userId": user_role.userId,
        "roleId": user_role.roleId
    }).execute()
    
    if exists.data:
        raise HTTPException(status_code=400, detail="User already has this role")
    
    new_assignment = {"userId": user_role.userId, "roleId": user_role.roleId}
    res = supabase.table("epay_user_roles").insert(new_assignment).execute()
    return res.data[0]

@router.get("/", response_model=List[schemas.UserRoleResponse])
async def list_user_roles(
    skip: int = 0, 
    limit: int = 100, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_user_roles").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/user/{user_id}", response_model=List[schemas.UserRoleResponse])
async def get_roles_for_user(
    user_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_user_roles").select("*").eq("userId", user_id).execute()
    return result.data

@router.delete("/{user_role_id}")
async def remove_role_from_user(
    user_role_id: int, 
    current_user: dict = Depends(deps.get_current_user)
):
    result = supabase.table("epay_user_roles").delete().eq("userRoleId", user_role_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="UserRole assignment not found")
    return {"message": "Role removed from user"}
