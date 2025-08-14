from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from ...core.database import get_db
from ...core.config import settings
from ...schemas import UserCreate, User, Token, TokenData
from ...core.logger import logger

router = APIRouter()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # TODO: Get user from database
    # For now, return a mock user
    user = User(
        id=1,
        email="user@example.com",
        username=username,
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow()
    )
    
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=User)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    
    try:
        # TODO: Check if user already exists
        # TODO: Create user in database
        
        hashed_password = get_password_hash(user_data.password)
        
        # Mock user creation
        logger.info(f"User registration attempt: {user_data.email}")
        
        user = User(
            id=1,
            email=user_data.email,
            username=user_data.username,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow()
        )
        
        return user
        
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token"""
    
    try:
        # TODO: Authenticate user against database
        # For now, use mock authentication
        
        if username == "admin" and password == "admin":
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": username}, expires_delta=access_token_expires
            )
            
            logger.info(f"User logged in: {username}")
            
            return Token(access_token=access_token, token_type="bearer")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token"""
    
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}
