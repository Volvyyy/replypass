"""
Supabase クライアント設定
"""

from supabase import create_client, Client
from .config import settings


def get_supabase_client() -> Client:
    """Supabase サービスロールクライアントを取得"""
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key
    )


def get_supabase_anon_client() -> Client:
    """Supabase 匿名クライアントを取得（フロントエンドと同等）"""
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_anon_key
    )


# グローバルクライアントインスタンス（必要に応じて使用）
supabase_client = get_supabase_client()
supabase_anon_client = get_supabase_anon_client()