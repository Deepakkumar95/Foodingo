import logging
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ..models import ORMUser
from ..models.enums import UserType
from ..services.user_service import UserService
from ..security import create_access_token, decode_access_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_service = UserService()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    user_type: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> ORMUser:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = await user_service.get_user_by_user_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_current_admin_user(current_user: ORMUser = Depends(get_current_user)) -> ORMUser:
    if current_user.user_type != UserType.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
