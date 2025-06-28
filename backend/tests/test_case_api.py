"""
Test cases for Case API endpoints

Following t-wada TDD best practices
"""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.case import Case
from app.models.user import User
from app.repositories.case import CaseRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for API tests"""
    user = User(
        email="testuser@example.com",
        auth_id="test_auth_123",
        profile={"display_name": "Test User"}
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def authenticated_headers(test_user: User):
    """Create authentication headers for test requests"""
    # Mock JWT token that contains user_id
    mock_token = "mock_jwt_token"
    
    with patch("app.auth.dependencies.get_current_user") as mock_get_user:
        mock_get_user.return_value = {
            "user_id": str(test_user.id),
            "email": test_user.email
        }
        yield {"Authorization": f"Bearer {mock_token}"}


@pytest.fixture
async def test_cases(db_session: AsyncSession, test_user: User) -> list[Case]:
    """Create test cases for API tests"""
    cases = []
    
    case1 = Case(
        user_id=test_user.id,
        name="Work Project",
        partner_name="Boss",
        partner_type="colleague",
        my_position="team member",
        conversation_purpose="project planning"
    )
    
    case2 = Case(
        user_id=test_user.id,
        name="Personal Chat",
        partner_name="Friend",
        partner_type="friend",
        conversation_purpose="personal talk"
    )
    
    case3 = Case(
        user_id=test_user.id,
        name="Client Meeting",
        partner_name="Client A",
        partner_type="client",
        my_position="consultant",
        conversation_purpose="requirements discussion"
    )
    
    for case in [case1, case2, case3]:
        db_session.add(case)
        cases.append(case)
    
    await db_session.flush()
    for case in cases:
        await db_session.refresh(case)
    
    return cases


class TestCaseListAPI:
    """Test GET /api/cases endpoint"""
    
    async def test_get_cases_without_auth_returns_401(self, client: TestClient):
        """Test that GET /api/cases requires authentication"""
        response = client.get("/api/cases")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_cases_empty_list(self, client: TestClient, authenticated_headers: dict):
        """Test GET /api/cases with no cases returns empty list"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(uuid4()), "email": "test@example.com"}
            
            response = client.get("/api/cases", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "cases" in data
        assert "pagination" in data
        assert data["cases"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 20
    
    async def test_get_cases_default_pagination(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases with default pagination parameters"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            response = client.get("/api/cases", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 3  # All 3 test cases
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 20
        assert data["pagination"]["has_previous"] is False
        assert data["pagination"]["has_next"] is False
    
    async def test_get_cases_with_custom_pagination(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases with custom pagination parameters"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            # Request page 1 with limit 2
            response = client.get("/api/cases?page=1&limit=2", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 2  # Limited to 2 cases
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["has_previous"] is False
        assert data["pagination"]["has_next"] is True
    
    async def test_get_cases_page_2(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases page 2"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            # Request page 2 with limit 2
            response = client.get("/api/cases?page=2&limit=2", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 1  # Only 1 case left on page 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_previous"] is True
        assert data["pagination"]["has_next"] is False
    
    async def test_get_cases_filter_by_partner_type(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases with partner_type filter"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            response = client.get("/api/cases?partner_type=friend", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 1
        assert data["cases"][0]["partner_type"] == "friend"
        assert data["pagination"]["total"] == 1
    
    async def test_get_cases_search_by_name(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases with search parameter"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            response = client.get("/api/cases?search=Work", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 1
        assert "Work" in data["cases"][0]["name"]
        assert data["pagination"]["total"] == 1
    
    async def test_get_cases_search_by_partner_name(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test GET /api/cases search by partner name"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            response = client.get("/api/cases?search=Boss", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 1
        assert data["cases"][0]["partner_name"] == "Boss"
    
    async def test_get_cases_with_invalid_pagination_params(self, client: TestClient, authenticated_headers: dict):
        """Test GET /api/cases with invalid pagination parameters"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(uuid4()), "email": "test@example.com"}
            
            # Test negative page
            response = client.get("/api/cases?page=-1", headers=authenticated_headers)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test zero page
            response = client.get("/api/cases?page=0", headers=authenticated_headers)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test limit too high
            response = client.get("/api/cases?limit=101", headers=authenticated_headers)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test negative limit
            response = client.get("/api/cases?limit=-1", headers=authenticated_headers)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_get_cases_returns_correct_case_structure(self, client: TestClient, authenticated_headers: dict, test_cases: list[Case]):
        """Test that GET /api/cases returns cases with correct structure"""
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_cases[0].user_id), "email": "test@example.com"}
            
            response = client.get("/api/cases", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        case = data["cases"][0]
        required_fields = [
            "id", "user_id", "name", "partner_name", "partner_type",
            "my_position", "conversation_purpose", "case_metadata",
            "created_at", "updated_at", "deleted_at", "is_deleted"
        ]
        
        for field in required_fields:
            assert field in case
        
        # Verify types
        assert isinstance(case["is_deleted"], bool)
        assert case["is_deleted"] is False  # Should not include deleted cases by default
        assert isinstance(case["case_metadata"], dict)
    
    async def test_get_cases_excludes_deleted_by_default(self, client: TestClient, authenticated_headers: dict, test_user: User, db_session: AsyncSession):
        """Test that GET /api/cases excludes soft-deleted cases by default"""
        # Create a deleted case
        deleted_case = Case(
            user_id=test_user.id,
            name="Deleted Case",
            partner_name="Deleted Partner"
        )
        deleted_case.soft_delete()
        db_session.add(deleted_case)
        await db_session.flush()
        
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_user.id), "email": "test@example.com"}
            
            response = client.get("/api/cases", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should not contain the deleted case
        case_names = [case["name"] for case in data["cases"]]
        assert "Deleted Case" not in case_names
    
    async def test_get_cases_includes_deleted_when_requested(self, client: TestClient, authenticated_headers: dict, test_user: User, db_session: AsyncSession):
        """Test that GET /api/cases can include deleted cases when explicitly requested"""
        # Create a deleted case
        deleted_case = Case(
            user_id=test_user.id,
            name="Deleted Case",
            partner_name="Deleted Partner"
        )
        deleted_case.soft_delete()
        db_session.add(deleted_case)
        await db_session.flush()
        
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_user.id), "email": "test@example.com"}
            
            response = client.get("/api/cases?include_deleted=true", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should contain the deleted case
        case_names = [case["name"] for case in data["cases"]]
        assert "Deleted Case" in case_names
        
        # Find the deleted case and verify it's marked as deleted
        deleted_case_data = next(case for case in data["cases"] if case["name"] == "Deleted Case")
        assert deleted_case_data["is_deleted"] is True
        assert deleted_case_data["deleted_at"] is not None


class TestCaseListAPIPerformance:
    """Test performance-related aspects of case list API"""
    
    async def test_get_cases_large_dataset_performance(self, client: TestClient, authenticated_headers: dict, test_user: User, db_session: AsyncSession):
        """Test that large datasets are handled efficiently"""
        # Create many test cases
        cases = []
        for i in range(50):
            case = Case(
                user_id=test_user.id,
                name=f"Case {i:03d}",
                partner_name=f"Partner {i:03d}",
                partner_type="test"
            )
            cases.append(case)
            db_session.add(case)
        
        await db_session.flush()
        
        with patch("app.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"user_id": str(test_user.id), "email": "test@example.com"}
            
            # Test with pagination
            response = client.get("/api/cases?page=1&limit=10", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["cases"]) == 10  # Should be limited to 10
        assert data["pagination"]["total"] == 50
        assert data["pagination"]["total_pages"] == 5