"""
Reply Pass Backend Configuration
Pydantic settingsを使用した環境変数管理
"""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""

    # 基本設定
    environment: str = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="DEBUG")

    # Supabase設定
    supabase_url: str = Field(default="placeholder")
    supabase_service_key: str = Field(default="placeholder")
    supabase_anon_key: str = Field(default="placeholder")
    supabase_jwt_secret: str = Field(default="placeholder")

    # データベース設定
    database_url: str = Field(default="placeholder")
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)

    # AI/LLM設定
    gemini_api_key: str = Field(default="placeholder")
    default_gemini_model: str = Field(default="gemini-2.0-flash")
    high_quality_gemini_model: str = Field(default="gemini-2.5-flash")
    ocr_gemini_model: str = Field(default="gemini-2.5-flash-lite")
    gemini_thinking_model: str = Field(default="gemini-2.0-flash-thinking")

    # Stripe設定
    stripe_secret_key: str = Field(default="placeholder")
    stripe_webhook_secret: str = Field(default="placeholder")
    stripe_price_id_pro: str = Field(default="placeholder")
    stripe_price_id_unlimited: str = Field(default="placeholder")

    # Redis設定
    redis_url: str = Field(default="redis://localhost:6379/0")

    # セキュリティ設定
    jwt_secret_key: str = Field(default="development-secret")
    jwt_expiration_seconds: int = Field(default=3600)
    password_salt_rounds: int = Field(default=12)

    # CORS設定
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"]
    )
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: List[str] = Field(
        default=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key",
            "User-Agent",
            "X-CSRF-Token",
            "X-Client-Version",
        ]
    )
    cors_expose_headers: List[str] = Field(
        default=[
            "X-Response-Time",
            "X-API-Version",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Request-ID",
        ]
    )

    # セキュリティ設定（2025年強化版）
    csp_policy: str = Field(
        default="default-src 'none'; script-src 'none'; style-src 'none'; img-src 'none'; font-src 'none'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none';"
    )
    permissions_policy: str = Field(
        default="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
    )

    # Cross-Origin policies (2025年標準)
    cross_origin_embedder_policy: str = Field(default="require-corp")
    cross_origin_opener_policy: str = Field(default="same-origin")
    cross_origin_resource_policy: str = Field(default="cross-origin")

    # レート制限設定（階層化）
    rate_limit_backend: str = Field(default="memory")
    basic_rate_limit_per_minute: int = Field(default=60)
    generation_rate_limit_per_minute: int = Field(default=5)
    auth_rate_limit_per_minute: int = Field(default=10)
    upload_rate_limit_per_minute: int = Field(default=3)
    webhook_rate_limit_per_minute: int = Field(default=100)

    # エンドポイント別レート制限設定
    rate_limits: dict[str, int] = Field(
        default={
            "/api/auth/": 10,
            "/api/upload/": 3,
            "/api/generate/": 5,
            "/api/webhooks/": 100,
            "default": 60,
        }
    )

    # ファイルアップロード設定
    max_file_size: int = Field(default=10485760)  # 10MB
    allowed_file_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"]
    )

    # 開発設定
    debug_mode: bool = Field(default=False)
    sql_echo: bool = Field(default=False)
    enable_docs: bool = Field(default=True)
    test_mode: bool = Field(default=False)

    # Supabase CLI・OAuth設定
    next_public_site_url: str = Field(default="http://localhost:3000")
    google_client_id: str = Field(default="placeholder-google-client-id")
    google_client_secret: str = Field(default="placeholder-google-client-secret")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_allow_methods(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip().upper() for item in v.split(",")]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_allow_headers(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @field_validator("cors_expose_headers", mode="before")
    @classmethod
    def parse_cors_expose_headers(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# 設定インスタンスを作成（シングルトン）
settings = Settings()


# 設定の検証とログ出力
def validate_settings() -> None:
    """設定の検証"""
    required_fields = [
        "supabase_url",
        "supabase_service_key",
        "supabase_jwt_secret",
        "gemini_api_key",
        "stripe_secret_key",
        "jwt_secret_key",
    ]

    missing_fields = []
    for field in required_fields:
        value = getattr(settings, field)
        if not value or value.startswith("placeholder"):
            missing_fields.append(field)

    if missing_fields:
        print(f"⚠️  以下の環境変数が設定されていません: {', '.join(missing_fields)}")
        print("開発用プレースホルダー値で動作しますが、実際のAPI機能は制限されます。")

    print(f"✅ 環境: {settings.environment}")
    print(f"✅ ポート: {settings.port}")
    print(f"✅ デバッグモード: {settings.debug_mode}")
    print(f"✅ APIドキュメント: {settings.enable_docs}")


if __name__ == "__main__":
    validate_settings()
