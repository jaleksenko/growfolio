from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from users.models import User, CreateUser, UpdateUser, DeleteUser, UserResponse, UpdateUserResponse, GetUserResponse, Token, EmailRequest, PasswordResetForm, PasswordChangeForm
from users.services import UserService
from users.dependencies import get_current_user
from core.database import get_session

from assets.models import BaseAsset
from watchlist.models import WatchlistAsset

import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(tags=["users"])

@router.get("/user", response_model=GetUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get information about the current user
    """
    return current_user

@router.get("/users", response_model=list[GetUserResponse])
async def get_users(session: AsyncSession = Depends(get_session)):
    """
    Fetch all users.
    """
    user_service = UserService(session)
    return await user_service.get_users()

@router.post("/auth", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: CreateUser,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to register a new user.
    """
    try:
        logging.info(f"Registering user: {user_data.username}")
        user_service = UserService(session)
        user_response = await user_service.register_user(user_data)
        logging.info(f"User registered successfully: {user_response.username}")
        return user_response
    except HTTPException as e:
        logging.error(f"HTTP exception occurred: {e.detail}")
        raise
    except Exception as e:
        logging.error("Internal Server Error during user registration:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@router.patch("/user", response_model=UpdateUserResponse)
async def update_user(
    update_user_request: UpdateUser,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Partially update the current user's `firstname` and `lastname`.
    """
    try:
        user_service = UserService(session)
        update_response = await user_service.update_user(current_user, update_user_request)
        return update_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during update")

@router.delete("/user")
async def delete_user(
    delete_user_request: DeleteUser,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes the current authenticated user after verifying the password.
    """
    try:
        user_service = UserService(session)
        await user_service.delete_user(current_user, delete_user_request)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")

@router.get("/auth/verify-email")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to verify an email.
    """
    try:
        user_service = UserService(session)
        result = await user_service.verify_email(token)
        return {"message": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and generate JWT token.
    """
    logging.info(f"Received login request for username: {form_data.username}")
    try:
        user_service = UserService(session)
        token = await user_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )
        logging.info(f"Login successful for username: {form_data.username}")
        return token
    except ValueError as e:
        logging.error(f"Authentication failed for username: {form_data.username}, Reason: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logging.error(f"Internal Server Error during login for username: {form_data.username}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.post("/auth/refresh-token", response_model=Token)
async def refresh_token(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        user_service = UserService(session)
        new_token = await user_service.extract_and_refresh_access_token(request)
        return new_token
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Could not refresh token"
        )

@router.post("/auth/password-reset")
async def request_password_reset(
    request: EmailRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to request a password reset.
    """
    try:
        user_service = UserService(session)
        reset_link = await user_service.request_password_reset(request.email)
        return {"message": "Password reset link sent", "reset_link": reset_link}
    except ValueError as e:
        logging.error(f"Password reset request failed: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logging.error(f"Internal Server Error during password reset request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@router.post("/auth/password-reset-form")
async def reset_password_form(
    request: PasswordResetForm,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to reset the password using a valid token.
    """
    try:
        user_service = UserService(session)
        await user_service.reset_password(request)
        return {"message": "Password has been reset successfully."}
    except ValueError as e:
        logging.error(f"Password reset failed: {e}", exc_info=True)
        raise
    except HTTPException as e:
        logging.error(f"HTTP exception during password reset: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Unexpected error during password reset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while resetting the password. Details: {e}",
        )

@router.post("/auth/password-change")
async def change_password(
    request: PasswordChangeForm,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to handle password change requests.
    """
    try:
        user_service = UserService(session)
        await user_service.change_password(
            user=current_user,
            request=request
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while changing the password.")