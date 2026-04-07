from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas
from ..core.supabase_client import supabase
from ..core import security, config
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate):
    # Check if user exists
    existing = supabase.table("epay_users").select("*").eq("emailId", user.emailId).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    
    # Create user in custom table
    new_user_data = {
        "emailId": user.emailId,
        "hashPassword": hashed_password,
        "fullName": user.fullName,
        "phoneNumber": user.phoneNumber,
        "algoPassword": "bcrypt",
        "isActive": True
    }
    
    try:
        result = supabase.table("epay_users").insert(new_user_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        new_user = result.data[0]
        
        # Assign Default User Role
        # Find or create 'user' role
        role_result = supabase.table("epay_roles").select("*").eq("roleName", "user").execute()
        if not role_result.data:
            # Create role if not exists
            role_result = supabase.table("epay_roles").insert({"roleName": "user"}).execute()
        
        default_role = role_result.data[0]
        
        # Create UserRole entry
        supabase.table("epay_user_roles").insert({
            "userId": new_user["userId"],
            "roleId": default_role["roleId"]
        }).execute()

        new_user["roles"] = [default_role]
        return new_user
    except Exception as e:
        print(f"DEBUG AUTH ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    result = supabase.table("epay_users").select("*").eq("emailId", form_data.username).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = result.data[0]
    if not security.verify_password(form_data.password, user["hashPassword"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Force password change if default
    if form_data.password == "12345678":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Default password detected. please use /auth/reset-password to change it."
        )

    # Validate Subscriptions
    bus_res = supabase.table("epay_business").select("businessId").eq("userId", user["userId"]).execute()
    if bus_res.data:
        business_ids = [b["businessId"] for b in bus_res.data]
        subs_res = supabase.table("epay_subscriptions").select("*").in_("businessId", business_ids).execute()
        
        if subs_res.data:
            # Check the first active/existing subscription plan
            sub = subs_res.data[0]
            now = datetime.now(timezone.utc)
            
            # Parse dates safely
            def parse_date(date_str):
                if not date_str: return None
                try:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    return None
                    
            start_date = parse_date(sub.get("subscriptionStartDate"))
            end_date = parse_date(sub.get("subscriptionEndDate"))
            
            if start_date and now < start_date:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your subscription has not started yet."
                )
                
            if end_date and now > end_date:
                if sub.get("subscriptionStatus") is not False:
                    supabase.table("epay_subscriptions").update({"subscriptionStatus": False}).eq("subscriptionId", sub["subscriptionId"]).execute()
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your subscription has expired. Please activate your account to continue."
                )

    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user["emailId"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password")
async def reset_password(request: schemas.ResetPassword):
    result = supabase.table("epay_users").select("*").eq("emailId", request.emailId).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result.data[0]
    if not security.verify_password(request.currentPassword, user["hashPassword"]):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    if request.newPassword == "12345678":
        raise HTTPException(status_code=400, detail="New password cannot be the default password")
        
    new_hashed = security.get_password_hash(request.newPassword)
    supabase.table("epay_users").update({"hashPassword": new_hashed}).eq("userId", user["userId"]).execute()
    
    return {"message": "Password changed successfully"}
