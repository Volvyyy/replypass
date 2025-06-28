"""
Test cases for Case repository

Following t-wada TDD best practices
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.user import User
from app.repositories.case import CaseRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        auth_id="auth_123",
        profile={"display_name": "Test User"}
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user

@pytest.fixture
def case_repo(db_session: AsyncSession) -> CaseRepository:
    """Create case repository instance"""
    return CaseRepository(db_session)


class TestCaseRepository:
    """Test Case repository basic functionality"""
    
    async def test_create_case(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test creating a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="Test Case",
            partner_name="John Doe"
        )
        await db_session.commit()
        
        assert case.id is not None
        assert case.user_id == test_user.id
        assert case.name == "Test Case"
        assert case.partner_name == "John Doe"
        assert case.case_metadata == {}
        assert case.deleted_at is None
    
    async def test_create_case_with_all_fields(self, case_repo: CaseRepository, test_user: User):
        """Test creating a case with all fields"""
        metadata = {"priority": "high", "tags": ["work", "urgent"]}
        
        case = await case_repo.create(
            user_id=test_user.id,
            name="Complete Case",
            partner_name="Jane Smith",
            partner_type="colleague",
            my_position="manager",
            conversation_purpose="project discussion",
            case_metadata=metadata
        )
        
        assert case.name == "Complete Case"
        assert case.partner_name == "Jane Smith"
        assert case.partner_type == "colleague"
        assert case.my_position == "manager"
        assert case.conversation_purpose == "project discussion"
        assert case.case_metadata == metadata
    
    async def test_get_by_id(self, case_repo: CaseRepository, test_user: User):
        """Test getting case by ID"""
        created_case = await case_repo.create(
            user_id=test_user.id,
            name="Test Case",
            partner_name="John"
        )
        
        fetched_case = await case_repo.get_by_id(created_case.id)
        
        assert fetched_case is not None
        assert fetched_case.id == created_case.id
        assert fetched_case.name == "Test Case"
        assert fetched_case.partner_name == "John"
    
    async def test_get_by_id_not_found(self, case_repo: CaseRepository):
        """Test getting non-existent case"""
        non_existent_id = uuid4()
        result = await case_repo.get_by_id(non_existent_id)
        
        assert result is None
    
    async def test_get_user_cases(self, case_repo: CaseRepository, test_user: User):
        """Test getting cases for a specific user"""
        # Create multiple cases
        case1 = await case_repo.create(
            user_id=test_user.id,
            name="Case 1",
            partner_name="Partner 1"
        )
        case2 = await case_repo.create(
            user_id=test_user.id,
            name="Case 2",
            partner_name="Partner 2"
        )
        
        # Create case for different user
        other_user_id = uuid4()
        await case_repo.create(
            user_id=other_user_id,
            name="Other Case",
            partner_name="Other Partner"
        )
        
        user_cases = await case_repo.get_user_cases(test_user.id)
        
        assert len(user_cases) == 2
        case_names = [case.name for case in user_cases]
        assert "Case 1" in case_names
        assert "Case 2" in case_names
        assert "Other Case" not in case_names
    
    async def test_update_case(self, case_repo: CaseRepository, test_user: User):
        """Test updating a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="Original Name",
            partner_name="Original Partner"
        )
        
        updated_case = await case_repo.update(
            case.id,
            name="Updated Name",
            partner_type="friend",
            my_position="colleague"
        )
        
        assert updated_case is not None
        assert updated_case.name == "Updated Name"
        assert updated_case.partner_name == "Original Partner"  # Unchanged
        assert updated_case.partner_type == "friend"
        assert updated_case.my_position == "colleague"
    
    async def test_update_case_not_found(self, case_repo: CaseRepository):
        """Test updating non-existent case"""
        non_existent_id = uuid4()
        result = await case_repo.update(non_existent_id, name="New Name")
        
        assert result is None
    
    async def test_soft_delete_case(self, case_repo: CaseRepository, test_user: User):
        """Test soft deleting a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="To Delete",
            partner_name="Partner"
        )
        
        success = await case_repo.soft_delete(case.id)
        
        assert success is True
        
        # Verify case is soft deleted
        deleted_case = await case_repo.get_by_id(case.id)
        assert deleted_case is not None
        assert deleted_case.deleted_at is not None
    
    async def test_soft_delete_case_not_found(self, case_repo: CaseRepository):
        """Test soft deleting non-existent case"""
        non_existent_id = uuid4()
        result = await case_repo.soft_delete(non_existent_id)
        
        assert result is False
    
    async def test_restore_case(self, case_repo: CaseRepository, test_user: User):
        """Test restoring a soft deleted case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="To Restore",
            partner_name="Partner"
        )
        
        # Soft delete first
        await case_repo.soft_delete(case.id)
        
        # Then restore
        success = await case_repo.restore(case.id)
        
        assert success is True
        
        # Verify case is restored
        restored_case = await case_repo.get_by_id(case.id)
        assert restored_case is not None
        assert restored_case.deleted_at is None
    
    async def test_hard_delete_case(self, case_repo: CaseRepository, test_user: User):
        """Test hard deleting a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="To Hard Delete",
            partner_name="Partner"
        )
        
        success = await case_repo.delete(case.id)
        
        assert success is True
        
        # Verify case is completely removed
        deleted_case = await case_repo.get_by_id(case.id)
        assert deleted_case is None


class TestCaseRepositoryFiltering:
    """Test Case repository filtering and search functionality"""
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user"""
        user = User(
            email="filter_test@example.com",
            auth_id="auth_filter_123",
            profile={"display_name": "Filter Test User"}
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def case_repo(self, db_session: AsyncSession) -> CaseRepository:
        """Create case repository instance"""
        return CaseRepository(db_session)
    
    @pytest.fixture
    async def sample_cases(self, case_repo: CaseRepository, test_user: User) -> List[Case]:
        """Create sample cases for filtering tests"""
        cases = []
        
        # Case 1: Work related
        case1 = await case_repo.create(
            user_id=test_user.id,
            name="Work Project",
            partner_name="Boss",
            partner_type="supervisor",
            conversation_purpose="project planning"
        )
        cases.append(case1)
        
        # Case 2: Personal
        case2 = await case_repo.create(
            user_id=test_user.id,
            name="Family Chat",
            partner_name="Mom",
            partner_type="family",
            conversation_purpose="personal"
        )
        cases.append(case2)
        
        # Case 3: Friend
        case3 = await case_repo.create(
            user_id=test_user.id,
            name="Friend Hangout",
            partner_name="Alice",
            partner_type="friend",
            conversation_purpose="social"
        )
        cases.append(case3)
        
        return cases
    
    async def test_get_user_cases_with_pagination(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test pagination in get_user_cases"""
        # Test first page
        first_page = await case_repo.get_user_cases(
            test_user.id, 
            limit=2, 
            offset=0
        )
        assert len(first_page) == 2
        
        # Test second page
        second_page = await case_repo.get_user_cases(
            test_user.id, 
            limit=2, 
            offset=2
        )
        assert len(second_page) == 1
    
    async def test_search_cases_by_name(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test searching cases by name"""
        results = await case_repo.search_cases(
            user_id=test_user.id,
            search_query="Work"
        )
        
        assert len(results) == 1
        assert results[0].name == "Work Project"
    
    async def test_search_cases_by_partner_name(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test searching cases by partner name"""
        results = await case_repo.search_cases(
            user_id=test_user.id,
            search_query="Alice"
        )
        
        assert len(results) == 1
        assert results[0].partner_name == "Alice"
    
    async def test_search_cases_by_purpose(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test searching cases by conversation purpose"""
        results = await case_repo.search_cases(
            user_id=test_user.id,
            search_query="social"
        )
        
        assert len(results) == 1
        assert results[0].conversation_purpose == "social"
    
    async def test_filter_by_partner_type(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test filtering cases by partner type"""
        results = await case_repo.get_user_cases(
            user_id=test_user.id,
            partner_type="family"
        )
        
        assert len(results) == 1
        assert results[0].partner_type == "family"
    
    async def test_exclude_deleted_cases(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test that soft deleted cases are excluded by default"""
        # Soft delete one case
        await case_repo.soft_delete(sample_cases[0].id)
        
        # Get all cases (should exclude deleted)
        active_cases = await case_repo.get_user_cases(test_user.id)
        
        assert len(active_cases) == 2
        case_ids = [str(case.id) for case in active_cases]
        assert str(sample_cases[0].id) not in case_ids
    
    async def test_include_deleted_cases(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test including soft deleted cases"""
        # Soft delete one case
        await case_repo.soft_delete(sample_cases[0].id)
        
        # Get all cases including deleted
        all_cases = await case_repo.get_user_cases(
            test_user.id, 
            include_deleted=True
        )
        
        assert len(all_cases) == 3
    
    async def test_count_user_cases(
        self, 
        case_repo: CaseRepository, 
        test_user: User, 
        sample_cases: List[Case]
    ):
        """Test counting user cases"""
        count = await case_repo.count_user_cases(test_user.id)
        assert count == 3
        
        # Count excluding deleted
        await case_repo.soft_delete(sample_cases[0].id)
        active_count = await case_repo.count_user_cases(test_user.id)
        assert active_count == 2
        
        # Count including deleted
        total_count = await case_repo.count_user_cases(
            test_user.id, 
            include_deleted=True
        )
        assert total_count == 3


class TestCaseRepositoryAdvanced:
    """Test advanced Case repository functionality"""
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user"""
        user = User(
            email="advanced_test@example.com",
            auth_id="auth_advanced_123",
            profile={"display_name": "Advanced Test User"}
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def case_repo(self, db_session: AsyncSession) -> CaseRepository:
        """Create case repository instance"""
        return CaseRepository(db_session)
    
    async def test_update_metadata(self, case_repo: CaseRepository, test_user: User):
        """Test updating case metadata"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="Metadata Test",
            partner_name="Partner",
            case_metadata={"initial": "value"}
        )
        
        updated_case = await case_repo.update_metadata(
            case.id,
            {"new_key": "new_value", "initial": "updated_value"}
        )
        
        assert updated_case is not None
        assert updated_case.case_metadata["new_key"] == "new_value"
        assert updated_case.case_metadata["initial"] == "updated_value"
    
    async def test_get_recent_cases(self, case_repo: CaseRepository, test_user: User):
        """Test getting recently updated cases"""
        # Create cases with different update times
        case1 = await case_repo.create(
            user_id=test_user.id,
            name="Old Case",
            partner_name="Partner1"
        )
        
        case2 = await case_repo.create(
            user_id=test_user.id,
            name="Recent Case",
            partner_name="Partner2"
        )
        
        # Update case1 to make it more recent
        await case_repo.update(case1.id, conversation_purpose="updated")
        
        recent_cases = await case_repo.get_recent_cases(test_user.id, limit=1)
        
        assert len(recent_cases) == 1
        assert recent_cases[0].id == case1.id
    
    async def test_get_partner_types(self, case_repo: CaseRepository, test_user: User):
        """Test getting unique partner types for a user"""
        await case_repo.create(
            user_id=test_user.id,
            name="Case 1",
            partner_name="Partner1",
            partner_type="friend"
        )
        
        await case_repo.create(
            user_id=test_user.id,
            name="Case 2",
            partner_name="Partner2",
            partner_type="colleague"
        )
        
        await case_repo.create(
            user_id=test_user.id,
            name="Case 3",
            partner_name="Partner3",
            partner_type="friend"  # Duplicate
        )
        
        partner_types = await case_repo.get_partner_types(test_user.id)
        
        assert len(partner_types) == 2
        assert "friend" in partner_types
        assert "colleague" in partner_types
    
    async def test_bulk_update_metadata(self, case_repo: CaseRepository, test_user: User):
        """Test bulk updating metadata for multiple cases"""
        case1 = await case_repo.create(
            user_id=test_user.id,
            name="Case 1",
            partner_name="Partner1"
        )
        
        case2 = await case_repo.create(
            user_id=test_user.id,
            name="Case 2",
            partner_name="Partner2"
        )
        
        case_ids = [case1.id, case2.id]
        metadata_update = {"bulk_updated": True, "timestamp": "2025-01-01"}
        
        count = await case_repo.bulk_update_metadata(case_ids, metadata_update)
        
        assert count == 2
        
        # Verify updates
        updated_case1 = await case_repo.get_by_id(case1.id)
        updated_case2 = await case_repo.get_by_id(case2.id)
        
        assert updated_case1.case_metadata["bulk_updated"] is True
        assert updated_case2.case_metadata["bulk_updated"] is True