# users/models.py

from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from users.validators import validate_password


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    firstname: str
    lastname: str
    email: EmailStr = Field(unique=True, nullable=False)
    email_verified: bool = False
    hashed_password: str | None = None
    provider: str = "local"
    created_at: datetime | None = None 
    # created_at: datetime = Field(default_factory=datetime.utcnow, nullable=True)

    # Relations for watchlist
    watchlists: list["Watchlist"] = Relationship(back_populates="user")
    # Relations for portfolio
    portfolios: list["Portfolio"] = Relationship(back_populates="user")


    def __init__(self, **kwargs):
        """
        A constructor to set the value of created_at if it is not provided in the input data.
        """
        super().__init__(**kwargs)
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class CreateUser(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        return validate_password(value)

class UserResponse(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    email_verified: bool
    access_token: str
    token_type: str = "bearer"

class UpdateUser(BaseModel):
    firstname: str | None = None
    lastname: str | None = None

class UpdateUserResponse(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    access_token: str | None = None
    token_type: str = "bearer"
    
class DeleteUser(BaseModel):
    password: str

class GetUserResponse(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    email_verified: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    exp: datetime

class EmailRequest(BaseModel):
    email: EmailStr

class EmailData(BaseModel):
    to_email: EmailStr
    subject: str
    template_name: str
    username: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    link: str | None = None

class PasswordResetForm(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, value: str) -> str:
        return validate_password(value)

class PasswordChangeForm(BaseModel):
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, value: str) -> str:
        return validate_password(value)
