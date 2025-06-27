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
    allowed_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:3001"])
    
    # レート制限設定
    rate_limit_backend: str = Field(default="memory")
    basic_rate_limit_per_minute: int = Field(default=60)
    generation_rate_limit_per_minute: int = Field(default=5)
    
    # ファイルアップロード設定
    max_file_size: int = Field(default=10485760)  # 10MB
    allowed_file_types: List[str] = Field(default=["image/jpeg", "image/png", "image/webp"])
    
    # 開発設定
    debug_mode: bool = Field(default=False)
    sql_echo: bool = Field(default=False)
    enable_docs: bool = Field(default=True)
    test_mode: bool = Field(default=False)
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @field_validator('allowed_file_types', mode='before')
    @classmethod
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# 設定インスタンスを作成（シングルトン）
settings = Settings()


# 設定の検証とログ出力
def validate_settings():
    """設定の検証"""
    required_fields = [
        "supabase_url",
        "supabase_service_key",
        "supabase_jwt_secret",
        "gemini_api_key",
        "stripe_secret_key",
        "jwt_secret_key"
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