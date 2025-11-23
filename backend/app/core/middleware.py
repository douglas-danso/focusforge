"""
Authentication and security middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication errors gracefully
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Paths that don't require authentication
        self.public_paths = {
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health",
            "/orchestrator/status"
        }
        
        # Path prefixes that don't require authentication
        self.public_prefixes = [
            "/api/v1/auth/",
            "/static/",
            "/favicon.ico"
        ]
    
    def is_public_path(self, path: str) -> bool:
        """Check if path is public and doesn't require authentication"""
        
        # Exact match
        if path in self.public_paths:
            return True
        
        # Prefix match
        for prefix in self.public_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle authentication errors"""
        
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # Handle authentication errors with better error messages
            if exc.status_code == status.HTTP_401_UNAUTHORIZED:
                
                path = request.url.path
                
                # If it's a public path, this shouldn't happen
                if self.is_public_path(path):
                    logger.error(f"Authentication error on public path: {path}")
                    return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={
                            "success": False,
                            "error": "Internal authentication error",
                            "message": "Authentication error on public endpoint"
                        }
                    )
                
                # For protected endpoints, provide helpful error message
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "Authentication required",
                        "message": "This endpoint requires authentication. Please log in first.",
                        "auth_endpoints": {
                            "google_auth_url": "/api/v1/auth/google/url",
                            "google_callback": "/api/v1/auth/google/callback",
                            "verify_token": "/api/v1/auth/verify",
                            "user_info": "/api/v1/auth/me"
                        },
                        "instructions": [
                            "1. Get Google OAuth URL from /api/v1/auth/google/url",
                            "2. Complete OAuth flow and get authorization code",
                            "3. Exchange code for JWT token at /api/v1/auth/google/callback",
                            "4. Include token in Authorization header: 'Bearer <token>'"
                        ]
                    }
                )
            
            # Re-raise other HTTP exceptions
            raise exc
            
        except Exception as exc:
            # Log unexpected errors
            logger.error(f"Unexpected error in authentication middleware: {exc}")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )
