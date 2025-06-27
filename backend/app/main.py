"""
Reply Pass Backend API
メイン FastAPI アプリケーション

Compatible with Supabase Auth 2025 and Next.js 15
"""

import logging
from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.auth.dependencies import get_current_user
from app.config import settings, validate_settings
from app.middleware.auth import AuthMiddleware, RateLimitMiddleware
from app.middleware.cors_handler import AdvancedCORSMiddleware
from app.middleware.logging_middleware import StructuredLoggingMiddleware
from app.middleware.request_validator import RequestValidationMiddleware
from app.middleware.security import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    openapi_url="/openapi.json" if settings.enable_docs else None,
    debug=settings.debug_mode,
    swagger_ui_parameters=(
        {
            "docExpansion": "none",
            "deepLinking": True,
            "persistAuthorization": True,
            "displayOperationId": True,
        }
        if settings.enable_docs
        else None
    ),
)

# Middleware order is critical! (Applied in reverse order)
# 1. Logging (outermost - logs everything)
app.add_middleware(StructuredLoggingMiddleware)

# 2. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Trusted host validation (production only)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=(
            settings.allowed_hosts if hasattr(settings, "allowed_hosts") else ["*"]
        ),
    )

# 5. Request validation
app.add_middleware(RequestValidationMiddleware)

# 6. Rate limiting
app.add_middleware(
    RateLimitMiddleware, requests_per_minute=settings.basic_rate_limit_per_minute
)

# 7. Authentication
app.add_middleware(AuthMiddleware)

# 8. CORS (innermost - needs to see authenticated requests)
app.add_middleware(AdvancedCORSMiddleware)

# Include API routers
app.include_router(auth_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    """
    logger.info(f"Starting Reply Pass API v1.0.0 in {settings.environment} mode")
    logger.info(f"CORS allowed origins: {settings.allowed_origins}")
    logger.info(f"Rate limiting: {settings.basic_rate_limit_per_minute} req/min")

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Verify external service connections


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    """
    logger.info("Shutting down Reply Pass API")

    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Flush any pending logs


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Reply Pass API v1.0.0",
        "status": "healthy",
        "auth": "Supabase Auth 2025 Ready",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    health_status = {
        "status": "healthy",
        "service": "reply-pass-api",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "supabase_auth": True,
            "jwt_validation": True,
            "rate_limiting": True,
            "security_headers": True,
            "request_validation": True,
            "structured_logging": True,
            "cors_enabled": True,
        },
        "middleware": {
            "security_headers": "active",
            "cors": "configured",
            "rate_limiting": "active",
            "request_validation": "active",
            "logging": "active",
            "compression": "gzip",
        },
    }

    # TODO: Add database health check
    # TODO: Add Redis health check
    # TODO: Add external service health checks

    return health_status


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


# Error handlers
@app.exception_handler(400)
async def bad_request_handler(request, exc):
    return JSONResponse(
        status_code=400, content={"error": "Bad request", "detail": str(exc)}
    )


@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"error": "Unauthorized", "detail": "Authentication required"},
    )


@app.exception_handler(403)
async def forbidden_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={"error": "Forbidden", "detail": "Insufficient permissions"},
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404, content={"error": "Not found", "detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )
