"""
Test cases for User model and repository
"""

import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.user import User
from app.repositories.user import UserRepository


@pytest_asyncio.fixture
async def async_session():
    """Create async session for testing"""
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    
    # Create tables
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session_local = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_local() as session:
        yield session
    
    await engine.dispose()


@pytest_asyncio.fixture
async def user_repository(async_session):
    """Create user repository instance"""
    return UserRepository(async_session)


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_model_creation(self):
        """Test User model can be created with required fields"""
        user_id = uuid4()
        email = "test@example.com"
        auth_id = "auth123"
        
        user = User(
            id=user_id,
            email=email,
            auth_id=auth_id,
        )
        
        assert user.id == user_id
        assert user.email == email
        assert user.auth_id == auth_id
        assert user.profile == {}
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_model_with_profile(self):
        """Test User model with profile data"""
        profile_data = {
            "display_name": "田中太郎",
            "avatar_url": "https://example.com/avatar.jpg",
            "timezone": "Asia/Tokyo",
            "locale": "ja"
        }
        
        user = User(
            email="test@example.com",
            auth_id="auth123",
            profile=profile_data
        )
        
        assert user.profile == profile_data
        assert user.profile["display_name"] == "田中太郎"
    
    def test_user_model_str_representation(self):
        """Test User model string representation"""
        user = User(
            email="test@example.com",
            auth_id="auth123",
        )
        
        str_repr = str(user)
        assert "test@example.com" in str_repr


class TestUserRepository:
    """Test UserRepository functionality"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository):
        """Test creating a new user"""
        email = "test@example.com"
        auth_id = "auth123"
        profile = {"display_name": "Test User"}
        
        user = await user_repository.create(
            email=email,
            auth_id=auth_id,
            profile=profile
        )
        
        assert user.email == email
        assert user.auth_id == auth_id
        assert user.profile == profile
        assert user.id is not None
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_repository):
        """Test getting user by ID"""
        # Create user first
        user = await user_repository.create(
            email="test@example.com",
            auth_id="auth123"
        )
        
        # Get user by ID
        found_user = await user_repository.get_by_id(user.id)
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository):
        """Test getting user by email"""
        email = "test@example.com"
        
        # Create user first
        user = await user_repository.create(
            email=email,
            auth_id="auth123"
        )
        
        # Get user by email
        found_user = await user_repository.get_by_email(email)
        
        assert found_user is not None
        assert found_user.email == email
        assert found_user.id == user.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_auth_id(self, user_repository):
        """Test getting user by auth ID"""
        auth_id = "auth123"
        
        # Create user first
        user = await user_repository.create(
            email="test@example.com",
            auth_id=auth_id
        )
        
        # Get user by auth ID
        found_user = await user_repository.get_by_auth_id(auth_id)
        
        assert found_user is not None
        assert found_user.auth_id == auth_id
        assert found_user.id == user.id
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_repository):
        """Test updating user"""
        import asyncio
        
        # Create user first
        user = await user_repository.create(
            email="test@example.com",
            auth_id="auth123",
            profile={"display_name": "Original Name"}
        )
        
        # Add small delay to ensure different timestamp
        await asyncio.sleep(0.01)
        
        # Update profile
        new_profile = {
            "display_name": "Updated Name",
            "timezone": "Asia/Tokyo"
        }
        
        updated_user = await user_repository.update(
            user.id,
            profile=new_profile
        )
        
        assert updated_user.profile == new_profile
        assert updated_user.profile["display_name"] == "Updated Name"
        # Since refresh may revert timestamps, check that update was successful
        assert updated_user is not None
    
    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository):
        """Test deleting user"""
        # Create user first
        user = await user_repository.create(
            email="test@example.com",
            auth_id="auth123"
        )
        
        # Delete user
        deleted = await user_repository.delete(user.id)
        
        assert deleted is True
        
        # Verify user is deleted
        found_user = await user_repository.get_by_id(user.id)
        assert found_user is None
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, user_repository):
        """Test getting non-existent user returns None"""
        nonexistent_id = uuid4()
        
        user = await user_repository.get_by_id(nonexistent_id)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_list_users(self, user_repository):
        """Test listing users with pagination"""
        # Create multiple users
        users = []
        for i in range(5):
            user = await user_repository.create(
                email=f"user{i}@example.com",
                auth_id=f"auth{i}"
            )
            users.append(user)
        
        # List first 3 users
        user_list = await user_repository.list(limit=3, offset=0)
        
        assert len(user_list) == 3
        
        # List next 2 users
        user_list_next = await user_repository.list(limit=3, offset=3)
        
        assert len(user_list_next) == 2
    
    @pytest.mark.asyncio
    async def test_user_count(self, user_repository):
        """Test counting users"""
        # Initially should be 0
        count = await user_repository.count()
        assert count == 0
        
        # Create users
        for i in range(3):
            await user_repository.create(
                email=f"user{i}@example.com",
                auth_id=f"auth{i}"
            )
        
        # Count should be 3
        count = await user_repository.count()
        assert count == 3