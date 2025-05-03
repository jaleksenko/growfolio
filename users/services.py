from fastapi import Request, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from users.repositories import UserRepository
from users.models import User, CreateUser, UpdateUser, DeleteUser, UpdateUserResponse, UserResponse, GetUserResponse, EmailData, Token, PasswordResetForm, PasswordChangeForm
from users.utils import hash_password, create_access_token, decode_token, get_refresh_token_from_request, construct_link, send_email, verify_password

import logging

logging.basicConfig(level=logging.DEBUG)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_user(self, user_data: CreateUser) -> User:
        """Hashes the password and creates a new user."""
        try:
            logging.info(f"Creating user: {user_data.username}")
            hashed_password = hash_password(user_data.password)
            logging.debug(f"Hashed password: {hashed_password}")
            user = User(
                username=user_data.username,
                firstname=user_data.firstname,
                lastname=user_data.lastname,
                email=user_data.email,
                email_verified=False,
                hashed_password=hashed_password,
            )
            # Save user first before creating a default watchlist
            user = await self.user_repo.create_user(user)
            return user
        except Exception as e:
            logging.error(f"Error creating user {user_data.username}: {e}")
            raise

    async def generate_token(self, user: User) -> Token:
        """
        Generates a JWT token for the authenticated user.
        """
        try:
            logging.info(f"Generating token for user: {user.username}")
            access_token = create_access_token({
                "sub": user.id,
                "username": user.username,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
            })
            logging.info(f"Token generated successfully for user: {user.username}")
            return Token(access_token=access_token, token_type="bearer")
        except Exception as e:
            logging.error(f"Error generating token for user: {user.username}, Error: {e}")
            raise

    async def register_user(self, user_data: CreateUser) -> UserResponse:
        """Registers a new user and returns their details with an access token."""
        logging.info(f"Received data: {user_data}")
        user = await self.create_user(user_data)

        # Generate the access token
        token = await self.generate_token(user)

        # Send the verification email with the verification token
        verification_link = construct_link(f"auth/verify-email?token={token.access_token}")
        email_data = EmailData(
            to_email=user.email,
            subject="Verify Your Email Address",
            template_name="email_verification",
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            link=verification_link,
        )
        send_email(email_data)

        response =  UserResponse(
            id=user.id,
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            email_verified=user.email_verified,
            access_token=token.access_token,
        )
        logging.debug(f"UserResponse: {response}")
        logging.info(f"UserResponse created successfully for user: {user.username}")
        return response

    async def update_user(self, user: User, update_user_request: UpdateUser) -> UpdateUserResponse:
        """
        Updates the user's `firstname` and `lastname` in the database and generates a response with a new token.
        """
        logging.info(f"Updating user: {user.username}")
        try:
            # Dynamically update `firstname` and `lastname` fields
            for key, value in update_user_request.dict(exclude_unset=True).items():
                # Skip if the value is None or matches the current user's value
                if value is None or getattr(user, key) == value:
                    continue

                # Update the attribute dynamically
                setattr(user, key, value)

            # Save the updated user through the repository
            updated_user = await self.user_repo.update_user(user)

            # Generate a new token using the existing `generate_token` method
            token = await self.generate_token(updated_user)

            # Return the updated user data with the new access token
            return UpdateUserResponse(
                firstname=updated_user.firstname,
                lastname=updated_user.lastname,
                email=updated_user.email,  # Email remains unchanged
                access_token=token.access_token
            )
        except Exception as e:
            logging.error(f"Unexpected error during user update: {e}")
            raise ValueError("Failed to update user details")

    async def delete_user(self, user: User, delete_user_request: DeleteUser) -> None:
        """
        Deletes the user after verifying the password.
        """
        logging.info(f"Attempting to delete user: {user.username}")

        try:
            # Verify the provided password using the existing utility
            if not verify_password(delete_user_request.password, user.hashed_password):
                raise ValueError("Incorrect password")

            # Delete the user via the repository
            await self.user_repo.delete_user(user)
            logging.info(f"User {user.username} deleted successfully")
        except ValueError as e:
            logging.error(f"Error deleting user {user.username}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during user deletion for {user.username}: {e}")
            raise ValueError("Failed to delete user")


    async def get_users(self) -> list[GetUserResponse]:
        """Fetches all users using the repository."""
        logging.info("Fetching all users from the database.")
        return await self.user_repo.get_all_users()
    
    async def verify_email(self, token: str) -> str:
        """
        Verifies the email from the given token and updates the user's email_verified status.
        """
        try:
            # Decode the token and extract the email
            payload = decode_token(token, token_type="access")
            email = str(payload.email)
            if not email:
                raise ValueError("Token does not contain an email.")
            
            # Fetch the user by email
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise ValueError("User not found.")
            
            # Check if the email is already verified
            if user.email_verified:
                return "Email is already verified."
            
            # Update the user's email_verified field
            await self.user_repo.update_user_email_verified(user)
            return "Email verified successfully."
        except ValueError as e:
            logging.error(f"Verification failed: {e}")
            raise ValueError(f"Email verification process encountered an error: {e}")

    async def authenticate_user(self, username: str, password: str) -> Token:
        """
        Authenticates a user by their username and password, and generates a token.
        """
        logging.info(f"Authenticating user: {username}")
        # Fetch the user
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            logging.error(f"User not found: {username}")
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logging.error(f"Invalid password for user: {username}")
            raise ValueError("Invalid credentials")
        
        # Ensure email is verified
        if not user.email_verified:
            logging.info(f"Email not verified for user: {username}")
            # Generate a temporary token for verification
            token = await self.generate_token(user)
            
            # Send the verification email with the verification token
            verification_link = construct_link(f"verify-email?token={token.access_token}")
            email_data = EmailData(
                to_email=user.email,
                subject="Verify Your Email Address",
                template_name="email_verification",
                username=user.username,
                firstname=user.firstname,
                lastname=user.lastname,
                link=verification_link,
            )
            send_email(email_data)
            logging.info(f"Verification email sent to: {user.email}")

            # Inform the user about the pending verification
            raise ValueError("Email not verified. A verification email has been sent.")
    
        # Generate token
        token = await self.generate_token(user)
        logging.info(f"Generated token for user: {username}")
        return token
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Validate the refresh token and generate a new access token.
        """
        try:
            # Decode and validate the refresh token
            payload = decode_token(refresh_token, token_type="refresh")
            
            # Fetch the user by email
            email = str(payload.email)
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise ValueError("Invalid refresh token")
            if not user.email_verified:
                raise ValueError("Email not verified")
            
            # Use the generate_token method to create a new access token
            return await self.generate_token(user)
        except ValueError as e:
            logging.error(f"Refresh token validation error: {e}")
            raise ValueError(f"Failed to refresh token: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during refresh token processing: {e}")
            raise ValueError("Internal server error while refreshing token")


    async def extract_and_refresh_access_token(self, request) -> Token:
        """
        Extract the refresh token from the request, validate it, and generate a new access token.
        """
        try:
            # Extract the refresh token from the request
            refresh_token = await get_refresh_token_from_request(request)
            
            # Use the refresh_access_token method to validate and refresh the token
            return await self.refresh_access_token(refresh_token)
        except ValueError as e:
            logging.error(f"Error extracting and refreshing access token: {e}")
            raise ValueError(f"Failed to refresh access token: {e}")
    
    async def request_password_reset(self, email: EmailStr) -> str:
        """
        Handles the logic for requesting a password reset.
        """
        logging.info(f"Password reset requested for email: {email}")
        # Find the user by email
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            logging.error(f"User with email {email} not found")
            raise ValueError("User not found")

        # Generate a token for password reset
        token = await self.generate_token(user)

        # Create a password reset link
        reset_link = construct_link(f"password-reset-form?token={token.access_token}")

        # Construct the email data
        email_data = EmailData(
            to_email=user.email,
            subject="Password Reset Request",
            template_name="password_reset",
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            link=reset_link,
        )

        # Send the email
        send_email(email_data)
        logging.info(f"Password reset email sent to {email}")

        return reset_link
    

    async def reset_password(self, request: PasswordResetForm) -> None:
        """
        Handles the logic for resetting a user's password.
        """
        logging.info("Resetting password")
        try:
            # Decode token and extract payload
            payload = decode_token(request.token, token_type="access")
            email = str(payload.email)
            if not email:
                raise ValueError("Token does not contain an email.")
            
            # Find the user by email
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                logging.error(f"User not found for email: {email}")
                raise ValueError("User not found.")

            # Check if the new password matches the current password
            if verify_password(request.new_password, user.hashed_password):
                logging.error("New password matches the old password")
                raise ValueError("New password must be different from the old password.")

            # Update the user's password securely
            hashed_password = hash_password(request.new_password)
            await self.user_repo.update_user_password(user, hashed_password)
            logging.info(f"Password reset successfully for user: {user.username}")

        except Exception as e:
            logging.error(f"Error resetting password: {e}", exc_info=True)
            raise ValueError(f"Error resetting password: {e}")
    
    async def change_password(self, user: User, request: PasswordChangeForm) -> None:
        """
        Handles changing the password for an authenticated user.

        Args:
            user (User): The authenticated user object.
            request (PasswordChangeForm): The new password request data.
        """
        logging.info(f"Changing password for user: {user.username}")

        try:
            # Ensure the new password is different
            if verify_password(request.new_password, user.hashed_password):
                raise ValueError("New password must be different from the old password.")

            # Hash the new password
            hashed_password = hash_password(request.new_password)

            # Update the user's password in the repository
            await self.user_repo.update_user_password(user, hashed_password)
            logging.info(f"Password changed successfully for user: {user.username}")

        except ValueError as e:
            logging.error(f"Password change failed: {e}")
            raise ValueError(str(e))
        except Exception as e:
            logging.error(f"Unexpected error during password change: {e}", exc_info=True)
            raise ValueError("Failed to change password due to an unexpected error.")


