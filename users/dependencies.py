from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database import get_session
from users.repositories import UserRepository
from users.models import User
from users.utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Decodes JWT token and fetches the current user from the database.
    """
    try:
        payload = decode_token(token)
        email = payload.email
        repo = UserRepository(session)
        user = await repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to authenticate user.")
