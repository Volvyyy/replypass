"""
FastAPI Dependencies for authentication and authorization
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from .config import settings
from .supabase_client import get_supabase_client

# HTTPBearer security scheme
security = HTTPBearer()


async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    JWT トークンを検証してユーザー情報を取得
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        Dict containing user information from JWT payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Supabase JWT secret を使用してトークンをデコード
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"  # Supabase のデフォルト audience
        )
        
        # 必要な要素が含まれているかチェック
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
            
        return payload
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(token_payload: Dict[str, Any] = Depends(verify_jwt_token)) -> Dict[str, Any]:
    """
    現在認証されているユーザーの情報を取得
    
    Args:
        token_payload: JWT payload from verify_jwt_token
        
    Returns:
        User information dictionary
    """
    user_id = token_payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    
    # Supabase から詳細なユーザー情報を取得（必要に応じて）
    try:
        supabase = get_supabase_client()
        response = supabase.auth.admin.get_user_by_id(user_id)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        return {
            "id": response.user.id,
            "email": response.user.email,
            "metadata": response.user.user_metadata,
            "app_metadata": response.user.app_metadata,
            "jwt_payload": token_payload
        }
        
    except Exception as e:
        # Supabase エラーの場合はJWTペイロードの情報のみ返す
        print(f"Warning: Could not fetch user details from Supabase: {e}")
        return {
            "id": user_id,
            "email": token_payload.get("email"),
            "jwt_payload": token_payload
        }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    オプショナル認証（認証必須でないエンドポイント用）
    
    Args:
        credentials: Optional Bearer token
        
    Returns:
        User information if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    try:
        payload = await verify_jwt_token(credentials)
        return await get_current_user(payload)
    except HTTPException:
        # 認証エラーの場合はNoneを返す（例外を投げない）
        return None


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    管理者権限が必要なエンドポイント用
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    app_metadata = current_user.get("app_metadata", {})
    user_role = app_metadata.get("role", "user")
    
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
        
    return current_user


class RateLimitChecker:
    """レート制限チェッカー（将来の実装用）"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
    
    async def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        # TODO: Redis や メモリベースのレート制限実装
        # 現在はパススルー
        return current_user


# よく使用される dependency の事前定義
require_auth = Depends(get_current_user)
optional_auth = Depends(get_optional_user)
require_admin_auth = Depends(require_admin)