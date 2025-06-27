"""
Reply Pass Backend API
メイン FastAPI アプリケーション
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, validate_settings

# 設定の検証
validate_settings()

app = FastAPI(
    title="Reply Pass API",
    description="AI-powered message reply generation service",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    debug=settings.debug_mode,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {"message": "Reply Pass API v1.0.0", "status": "healthy"}


@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "reply-pass-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)