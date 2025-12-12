from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User

router = APIRouter()

# Security configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool

    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate a user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Get the current always user from token"""
    print(f"🔑 Received token: {token[:50]}...")  # Debug

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"📦 Decoded payload: {payload}")  # Debug

        # JWT returns string, not int - need to convert
        user_id_str = payload.get("sub")
        print(f"👤 user_id_str: {user_id_str}, type: {type(user_id_str)}")  # Debug

        if user_id_str is None:
            print("❌ user_id_str is None")  # Debug
            raise credentials_exception

        # Convert to integer
        user_id = int(user_id_str)
        print(f"🔢 Converted user_id: {user_id}")  # Debug

        token_data = TokenData(user_id=user_id)
    except (JWTError, ValueError, TypeError) as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")  # Debug
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    print(f"🔍 User query result: {user}")  # Debug

    if user is None:
        print("❌ User not found in database")  # Debug
        raise credentials_exception

    if not user.is_active:
        print(f"❌ User {user.username} is not active")  # Debug
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    print(f"✅ Returning user: {user.username}")  # Debug
    return user


# Routes
@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Login endpoint - returns JWT token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},  # Explicit str conversion
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Register a new user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength (basic check)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Logout endpoint - client should discard the token
    Note: For stateless JWT, actual invalidation requires a token blacklist (not implemented)
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "username": current_user.username},  # Fixed: convert to str
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/password-reset")
async def request_password_reset(
    reset: PasswordReset,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Request password reset - sends email with reset token
    Note: Email sending not implemented - would require email service integration
    """
    user = db.query(User).filter(User.email == reset.email).first()

    # Always return success to prevent email enumeration
    if user:
        # TODO: Generate reset token with expiration
        # TODO: Store token in database or cache with expiration
        # TODO: Send email with reset link
        # Example: reset_token = create_access_token(
        #     data={"sub": user.id, "type": "password_reset"},
        #     expires_delta=timedelta(hours=1)
        # )
        pass

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset: PasswordResetConfirm,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Confirm password reset with token
    """
    try:
        payload = jwt.decode(reset.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")

        if token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Validate new password
        if len(reset.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )

        # Update password
        user.hashed_password = get_password_hash(reset.new_password)
        db.commit()

        return {"message": "Password reset successfully"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.post("/password-change")
async def change_password(
    password_change: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Change password for authenticated user
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(password_change.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    # Check if new password is different from current
    if verify_password(password_change.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
