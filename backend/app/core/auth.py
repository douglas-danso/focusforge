"""
Authentication system with Google OAuth and JWT tokens
"""

try:
    import jwt
    import httpx
except ImportError:
    jwt = None
    httpx = None

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
try:
    from fastapi import HTTPException, status, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
except ImportError:
    pass
import logging

from app.core.config import settings
from app.core.database import get_database
from app.models.schemas import User, UserCreate
from bson import ObjectId

logger = logging.getLogger(__name__)

# JWT Settings
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Google OAuth Settings
GOOGLE_OAUTH_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

security = HTTPBearer()


class GoogleOAuthToken(BaseModel):
    """Google OAuth token response"""
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: Optional[str] = None


class GoogleUserInfo(BaseModel):
    """Google user information"""
    id: str
    email: str
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None


class AuthToken(BaseModel):
    """JWT authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=JWT_EXPIRATION_HOURS * 3600)
    user_id: str
    email: str
    name: str


class AuthService:
    """Authentication service handling Google OAuth and JWT tokens"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient()
    
    async def exchange_google_code_for_token(
        self, authorization_code: str
    ) -> GoogleOAuthToken:
        """Exchange Google authorization code for access token"""
        try:
            token_data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            }
            
            response = await self.http_client.post(
                GOOGLE_OAUTH_URL, data=token_data
            )
            response.raise_for_status()
            
            token_info = response.json()
            return GoogleOAuthToken(**token_info)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Google OAuth token exchange failed: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code"
            )
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    async def get_google_user_info(self, access_token: str) -> GoogleUserInfo:
        """Get user information from Google using access token"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await self.http_client.get(GOOGLE_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            return GoogleUserInfo(**user_info)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Google user info fetch failed: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access token"
            )
        except Exception as e:
            logger.error(f"User info fetch error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User information retrieval failed"
            )
    
    def create_jwt_token(self, user_data: Dict[str, Any]) -> AuthToken:
        """Create JWT token for authenticated user"""
        try:
            # Token payload
            payload = {
                "sub": user_data["user_id"],  # Subject (user ID)
                "email": user_data["email"],
                "name": user_data["name"],
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                "type": "access_token"
            }
            
            # Create JWT token
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            
            return AuthToken(
                access_token=token,
                user_id=user_data["user_id"],
                email=user_data["email"],
                name=user_data["name"]
            )
            
        except Exception as e:
            logger.error(f"JWT token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def create_or_update_user(self, google_user: GoogleUserInfo, db) -> User:
        """Create or update user from Google user info"""
        try:
            # Check if user exists
            existing_user = await db.users.find_one({"email": google_user.email})
            
            if existing_user:
                # Update existing user
                update_data = {
                    "full_name": google_user.name,
                    "updated_at": datetime.utcnow()
                }
                
                # Update profile picture if available
                if google_user.picture:
                    update_data["profile_picture"] = google_user.picture
                
                await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": update_data}
                )
                
                # Fetch updated user
                updated_user = await db.users.find_one({"_id": existing_user["_id"]})
                return User(
                    id=str(updated_user["_id"]),
                    email=updated_user["email"],
                    username=updated_user["username"],
                    full_name=updated_user["full_name"],
                    is_active=updated_user.get("is_active", True),
                    created_at=updated_user["created_at"],
                    updated_at=updated_user["updated_at"]
                )
            else:
                # Create new user
                user_data = UserCreate(
                    email=google_user.email,
                    username=google_user.email.split("@")[0],  # Use email prefix as username
                    full_name=google_user.name,
                    password="google_oauth"  # Placeholder, not used for OAuth users
                )
                
                new_user_doc = {
                    "email": user_data.email,
                    "username": user_data.username,
                    "full_name": user_data.full_name,
                    "hashed_password": "google_oauth",  # OAuth users don't need password
                    "is_active": True,
                    "auth_provider": "google",
                    "google_id": google_user.id,
                    "profile_picture": google_user.picture,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await db.users.insert_one(new_user_doc)
                new_user_doc["_id"] = result.inserted_id
                
                return User(
                    id=str(new_user_doc["_id"]),
                    email=new_user_doc["email"],
                    username=new_user_doc["username"],
                    full_name=new_user_doc["full_name"],
                    is_active=new_user_doc["is_active"],
                    created_at=new_user_doc["created_at"],
                    updated_at=new_user_doc["updated_at"]
                )
                
        except Exception as e:
            logger.error(f"User creation/update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User management failed"
            )
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Global auth service instance
auth_service = AuthService()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database)
) -> str:
    """
    Dependency to get current authenticated user ID from JWT token
    Returns user_id string for use in endpoints
    """
    try:
        # Extract token from Bearer header
        token = credentials.credentials
        
        # Verify JWT token
        payload = auth_service.verify_jwt_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user still exists and is active
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            # If ObjectId conversion fails, try with string ID
            user = await db.users.find_one({"_id": user_id})
        
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user_details(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database)
) -> User:
    """
    Dependency to get full current user details from JWT token
    Returns User model with complete information
    """
    try:
        # Extract token from Bearer header
        token = credentials.credentials
        
        # Verify JWT token
        payload = auth_service.verify_jwt_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            # If ObjectId conversion fails, try with string ID
            user_doc = await db.users.find_one({"_id": user_id})
        
        if not user_doc or not user_doc.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return User(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            username=user_doc["username"],
            full_name=user_doc.get("full_name", ""),
            is_active=user_doc.get("is_active", True),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User details fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def get_google_oauth_url() -> str:
    """Generate Google OAuth authorization URL"""
    base_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"

