from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .core.supabase_client import supabase
from .core.config import settings
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(emailId=email)
    except JWTError:
        raise credentials_exception
    
    try:
        result = supabase.table("epay_users").select("*").eq("emailId", token_data.emailId).execute()
    except Exception as e:
        print(f"CRITICAL AUTH SUPABASE ERROR: Email={token_data.emailId}, Error={str(e)}")
        raise credentials_exception

    if not result.data:
        raise credentials_exception
    
    user = result.data[0]
    return user
