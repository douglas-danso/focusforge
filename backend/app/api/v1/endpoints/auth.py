"""
Authentication API endpoints for Google OAuth
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.core.auth import (
    auth_service, 
    get_current_user_from_token, 
    get_current_user_details,
    get_google_oauth_url,
    AuthToken
)
from app.core.database import get_database
from app.models.schemas import User

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth callback"""
    authorization_code: str = Field(..., description="Authorization code from Google")


class AuthResponse(BaseModel):
    """Authentication response with token and user info"""
    success: bool = True
    message: str
    token: AuthToken
    user: Dict[str, Any]


class GoogleOAuthUrlResponse(BaseModel):
    """Google OAuth URL response"""
    success: bool = True
    auth_url: str
    message: str = "Visit this URL to authenticate with Google"
    instructions: list = [
        "1. Click the authorization URL",
        "2. Sign in to your Google account", 
        "3. Grant the requested permissions",
        "4. Copy the authorization code from the redirect",
        "5. Use the code with the /auth/google/callback endpoint"
    ]


@router.get("/google/url", response_model=GoogleOAuthUrlResponse)
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        if not auth_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not available"
            )
        
        auth_url = get_google_oauth_url()
        
        return GoogleOAuthUrlResponse(
            auth_url=auth_url,
            message="Visit this URL to authenticate with Google"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}"
        )


@router.post("/google/callback", response_model=AuthResponse)
async def google_oauth_callback(
    auth_request: GoogleAuthRequest,
    db=Depends(get_database)
):
    """Handle Google OAuth callback and create user session"""
    try:
        # Exchange authorization code for access token
        google_token = await auth_service.exchange_google_code_for_token(
            auth_request.authorization_code
        )
        
        # Get user information from Google
        google_user = await auth_service.get_google_user_info(google_token.access_token)
        
        # Create or update user in database
        user = await auth_service.create_or_update_user(google_user, db)
        
        # Create JWT token for user
        jwt_token = auth_service.create_jwt_token({
            "user_id": user.id,
            "email": user.email,
            "name": user.full_name or user.username
        })
        
        return AuthResponse(
            message="Authentication successful",
            token=jwt_token,
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: User = Depends(get_current_user_details)
):
    """Get current authenticated user information"""
    return current_user


@router.post("/logout")
async def logout(
    current_user_id: str = Depends(get_current_user_from_token)
):
    """Logout current user (client should discard token)"""
    return {
        "success": True,
        "message": "Logged out successfully",
        "user_id": current_user_id,
        "instructions": "Please discard the authentication token on the client side"
    }


@router.get("/verify")
async def verify_token(
    current_user_id: str = Depends(get_current_user_from_token)
):
    """Verify if current token is valid"""
    return {
        "success": True,
        "message": "Token is valid",
        "user_id": current_user_id,
        "authenticated": True
    }


@router.get("/status")
async def auth_status():
    """Get authentication system status"""
    try:
        from app.core.config import settings
        
        google_configured = bool(
            settings.GOOGLE_CLIENT_ID and 
            settings.GOOGLE_CLIENT_SECRET and 
            settings.GOOGLE_REDIRECT_URI
        )
        
        return {
            "success": True,
            "authentication_enabled": True,
            "google_oauth_configured": google_configured,
            "jwt_enabled": True,
            "providers": ["google"],
            "message": "Authentication system is operational" if google_configured else "Google OAuth not fully configured"
        }
        
    except Exception as e:
        return {
            "success": False,
            "authentication_enabled": False,
            "error": str(e),
            "message": "Authentication system error"
        }
