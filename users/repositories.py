from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import NoResultFound
from users.models import User

import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_users(self) -> list[User]:
        """Fetches all users from the database."""
        query = select(User)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Fetches a user by their email.
        """
        try:
            query = select(User).where(User.email == email)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except NoResultFound:
            return None
    
    async def get_user_by_username(self, username: str) -> User | None:
        """
        Fetches a user by their username.
        """
        try:
            logging.info(f"Fetching user by username: {username}")
            query = select(User).where(User.username == username)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                logging.warning(f"No user found with username: {username}")
            return user
        except Exception as e:
            logging.error(f"Unexpected error occurred while fetching user by username: {username}. Error: {e}", exc_info=True)
            raise ValueError(f"Failed to fetch user by username {username}: {e}")
    
    async def create_user(self, user: User) -> User:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            logging.error(f"Failed to create user: {e}")
            raise ValueError(f"Failed to create user: {e}")

    async def update_user(self, user: User) -> User:
        """Commits changes to the user object."""
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            logging.error(f"Failed to update user: {user.id}, Error: {e}")
            await self.session.rollback()
            raise ValueError("Failed to update user")
    
    async def update_user_email_verified(self, user: User) -> None:
        """
        Updates the email_verified field of the user to True.
        """
        user.email_verified = True
        self.session.add(user)
        await self.session.commit()
    
    async def update_user_password(self, user: User, new_hashed_password: str) -> None:
        """
        Updates the user's password securely.
        """
        try:
            user.hashed_password = new_hashed_password
            self.session.add(user)
            logging.debug(f"Updating password for user: {user.email}")
            await self.session.commit()
            logging.info(f"Password updated successfully for user: {user.email}")
        except Exception as e:
            logging.error(f"Failed to update user password for {user.email}: {e}", exc_info=True)
            await self.session.rollback()
            raise ValueError(f"Failed to update user password: {e}")
    
    async def delete_user(self, user: User) -> None:
        """
        Deletes a user from the database.
        """
        try:
            await self.session.delete(user)
            await self.session.commit()
            logging.info(f"User {user.username} deleted successfully")
        except Exception as e:
            logging.error(f"Failed to delete user: {e}")
            await self.session.rollback()
            raise ValueError("Failed to delete user")

            

