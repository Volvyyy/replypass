"""
Simplified test cases for Case repository

Following t-wada TDD best practices
"""

import pytest
from uuid import uuid4
from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.user import User
from app.repositories.case import CaseRepository

pytestmark = pytest.mark.asyncio




class TestCaseRepositoryBasic:
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
    
    async def test_create_case_with_all_fields(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
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
        await db_session.commit()
        
        assert case.name == "Complete Case"
        assert case.partner_name == "Jane Smith"
        assert case.partner_type == "colleague"
        assert case.my_position == "manager"
        assert case.conversation_purpose == "project discussion"
        assert case.case_metadata == metadata
    
    async def test_get_by_id(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test getting case by ID"""
        created_case = await case_repo.create(
            user_id=test_user.id,
            name="Test Case",
            partner_name="John"
        )
        await db_session.commit()
        
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
    
    async def test_get_user_cases(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
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
        await db_session.commit()
        
        user_cases = await case_repo.get_user_cases(test_user.id)
        
        assert len(user_cases) == 2
        case_names = [case.name for case in user_cases]
        assert "Case 1" in case_names
        assert "Case 2" in case_names
    
    async def test_update_case(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test updating a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="Original Name",
            partner_name="Original Partner"
        )
        await db_session.commit()
        
        updated_case = await case_repo.update(
            case.id,
            name="Updated Name",
            partner_type="friend",
            my_position="colleague"
        )
        await db_session.commit()
        
        assert updated_case is not None
        assert updated_case.name == "Updated Name"
        assert updated_case.partner_name == "Original Partner"  # Unchanged
        assert updated_case.partner_type == "friend"
        assert updated_case.my_position == "colleague"
    
    async def test_soft_delete_case(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test soft deleting a case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="To Delete",
            partner_name="Partner"
        )
        await db_session.commit()
        
        success = await case_repo.soft_delete(case.id)
        await db_session.commit()
        
        assert success is True
        
        # Verify case is soft deleted
        deleted_case = await case_repo.get_by_id(case.id)
        assert deleted_case is not None
        assert deleted_case.deleted_at is not None
    
    async def test_restore_case(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test restoring a soft deleted case"""
        case = await case_repo.create(
            user_id=test_user.id,
            name="To Restore",
            partner_name="Partner"
        )
        await db_session.commit()
        
        # Soft delete first
        await case_repo.soft_delete(case.id)
        await db_session.commit()
        
        # Then restore
        success = await case_repo.restore(case.id)
        await db_session.commit()
        
        assert success is True
        
        # Verify case is restored
        restored_case = await case_repo.get_by_id(case.id)
        assert restored_case is not None
        assert restored_case.deleted_at is None
    
    async def test_count_user_cases(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test counting user cases"""
        # Create test cases
        await case_repo.create(
            user_id=test_user.id,
            name="Case 1",
            partner_name="Partner 1"
        )
        await case_repo.create(
            user_id=test_user.id,
            name="Case 2",
            partner_name="Partner 2"
        )
        await db_session.commit()
        
        count = await case_repo.count_user_cases(test_user.id)
        assert count == 2
    
    async def test_search_cases(self, case_repo: CaseRepository, test_user: User, db_session: AsyncSession):
        """Test searching cases"""
        await case_repo.create(
            user_id=test_user.id,
            name="Work Project",
            partner_name="Boss",
            conversation_purpose="project planning"
        )
        await case_repo.create(
            user_id=test_user.id,
            name="Personal Chat",
            partner_name="Friend",
            conversation_purpose="personal"
        )
        await db_session.commit()
        
        # Search by name
        work_results = await case_repo.search_cases(test_user.id, "Work")
        assert len(work_results) == 1
        assert work_results[0].name == "Work Project"
        
        # Search by partner
        friend_results = await case_repo.search_cases(test_user.id, "Friend")
        assert len(friend_results) == 1
        assert friend_results[0].partner_name == "Friend"