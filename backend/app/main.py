"""
Reply Pass Backend API
メイン FastAPI アプリケーション

Compatible with Supabase Auth 2025 and Next.js 15
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings, validate_settings
from app.middleware.auth import AuthMiddleware, RateLimitMiddleware
from app.auth.dependencies import get_current_user

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 設定の検証
validate_settings()

app = FastAPI(
    title="Reply Pass API",
    description="AI-powered message reply generation service with Supabase Auth integration",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    debug=settings.debug_mode,
)

# Add security middleware (order matters!)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    RateLimitMiddleware, 
    requests_per_minute=int(getattr(settings, 'basic_rate_limit_per_minute', 60))
)

# CORS設定 (after auth middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time", "X-API-Version"],
)


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Reply Pass API v1.0.0", 
        "status": "healthy",
        "auth": "Supabase Auth 2025 Ready"
    }


@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy", 
        "service": "reply-pass-api", 
        "version": "1.0.0",
        "features": {
            "supabase_auth": True,
            "jwt_validation": True,
            "rate_limiting": True,
            "security_headers": True
        }
    }


@app.get("/auth/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get authenticated user profile
    
    @security Requires valid Supabase JWT token
    @returns User profile information from JWT claims
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "metadata": current_user.get("user_metadata", {}),
    }


@app.get("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify JWT token validity
    
    @security Requires valid Supabase JWT token
    @returns Token verification status and user info
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "exp": current_user.get("exp"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
