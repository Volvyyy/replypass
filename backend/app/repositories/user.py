"""
User repository for database operations
"""

from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations
    
    Implements specific user-related database operations
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize user repository with async session
        
        Args:
            session: Async database session
        """
        super().__init__(User, session)
    
    async def create(
        self,
        email: str,
        auth_id: str,
        profile: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create a new user
        
        Args:
            email: User email address
            auth_id: Supabase Auth ID
            profile: Optional profile data
            
        Returns:
            Created User instance
        """
        if profile is None:
            profile = {}
        
        return await super().create(
            email=email,
            auth_id=auth_id,
            profile=profile
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email: Email address to search for
            
        Returns:
            User instance or None if not found
        """
        return await self.get_by_field("email", email)
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[User]:
        """
        Get user by Supabase Auth ID
        
        Args:
            auth_id: Supabase Auth ID to search for
            
        Returns:
            User instance or None if not found
        """
        return await self.get_by_field("auth_id", auth_id)
    
    async def update_profile(
        self,
        user_id: UUID,
        profile: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user profile
        
        Args:
            user_id: User UUID
            profile: New profile data
            
        Returns:
            Updated User instance or None if not found
        """
        return await self.update(user_id, profile=profile)
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email address already exists
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        stmt = select(User.id).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def auth_id_exists(self, auth_id: str) -> bool:
        """
        Check if auth ID already exists
        
        Args:
            auth_id: Supabase Auth ID to check
            
        Returns:
            True if auth ID exists, False otherwise
        """
        stmt = select(User.id).where(User.auth_id == auth_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def search_by_display_name(
        self,
        query: str,
        limit: int = 10
    ) -> list[User]:
        """
        Search users by display name
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching User instances
        """
        # PostgreSQL JSONB query for display_name
        stmt = (
            select(User)
            .where(User.profile["display_name"].astext.ilike(f"%{query}%"))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_users_by_timezone(self, timezone: str) -> list[User]:
        """
        Get users by timezone
        
        Args:
            timezone: Timezone to filter by
            
        Returns:
            List of User instances in the specified timezone
        """
        stmt = select(User).where(User.profile["timezone"].astext == timezone)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_users_by_locale(self, locale: str) -> list[User]:
        """
        Get users by locale
        
        Args:
            locale: Locale to filter by
            
        Returns:
            List of User instances with the specified locale
        """
        stmt = select(User).where(User.profile["locale"].astext == locale)
        result = await self.session.execute(stmt)
        return result.scalars().all()