import logging
from typing import Optional

from sqlalchemy import select

from ..database import get_session
from ..models import ORMUser
from utils.security import SecurityUtils

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session_factory=None, security_utils=None):
        self.session_factory = session_factory or get_session
        self.security = security_utils or SecurityUtils()

    async def get_user_by_user_id(self, user_id: str) -> Optional[ORMUser]:
        with self.session_factory() as session:
            return session.execute(
                select(ORMUser).where(ORMUser.user_id == user_id)
            ).scalars().first()

    async def create_user(self, user_id: str, password: str, name: str, email: str = None, phone: str = None, user_type: str = "customer") -> ORMUser:
        existing = await self.get_user_by_user_id(user_id)
        if existing:
            raise ValueError("User already exists")

        password_hash = self.security.hash_password(password)
        with self.session_factory() as session:
            user = ORMUser(
                user_id=user_id,
                name=name,
                email=email,
                phone=phone,
                user_type=user_type,
                password_hash=password_hash
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    async def authenticate_user(self, user_id: str, password: str) -> Optional[ORMUser]:
        user = await self.get_user_by_user_id(user_id)
        if not user:
            return None

        if self.security.verify_password(password, user.password_hash):
            return user

        logger.warning(f"Authentication failed for user {user_id}")
        return None
