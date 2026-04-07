from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas, deps
from ..core.supabase_client import supabase

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=schemas.RoleResponse)
async def create_role(role: schemas.RoleCreate, current_user: dict = Depends(deps.get_current_user)):
    # Check if role exists
    existing = supabase.table("epay_roles").select("*").eq("roleName", role.roleName).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    new_role = {"roleName": role.roleName}
    res = supabase.table("epay_roles").insert(new_role).execute()
    return res.data[0]

@router.get("/", response_model=List[schemas.RoleResponse])
async def read_roles(skip: int = 0, limit: int = 100, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_roles").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/{role_id}", response_model=schemas.RoleResponse)
async def read_role(role_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_roles").select("*").eq("roleId", role_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Role not found")
    return result.data[0]

@router.delete("/{role_id}")
async def delete_role(role_id: int, current_user: dict = Depends(deps.get_current_user)):
    result = supabase.table("epay_roles").delete().eq("roleId", role_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted"}
