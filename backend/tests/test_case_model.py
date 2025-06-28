"""
Test cases for Case model

Following t-wada TDD best practices
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.case import Case


class TestCaseModel:
    """Test Case model basic functionality"""

    def test_case_creation_minimal_required_fields(self):
        """Test creating a case with minimal required fields"""
        user_id = uuid4()
        case = Case(user_id=user_id, name="Test Case", partner_name="John Doe")

        assert case.user_id == user_id
        assert case.name == "Test Case"
        assert case.partner_name == "John Doe"
        assert case.partner_type is None
        assert case.my_position is None
        assert case.conversation_purpose is None
        assert case.case_metadata == {}
        assert case.deleted_at is None
        assert isinstance(case.created_at, datetime)
        assert isinstance(case.updated_at, datetime)

    def test_case_creation_all_fields(self):
        """Test creating a case with all fields"""
        user_id = uuid4()
        metadata = {"important": True, "priority": "high"}

        case = Case(
            user_id=user_id,
            name="Complete Test Case",
            partner_name="Jane Smith",
            partner_type="colleague",
            my_position="manager",
            conversation_purpose="project discussion",
            case_metadata=metadata,
        )

        assert case.user_id == user_id
        assert case.name == "Complete Test Case"
        assert case.partner_name == "Jane Smith"
        assert case.partner_type == "colleague"
        assert case.my_position == "manager"
        assert case.conversation_purpose == "project discussion"
        assert case.case_metadata == metadata
        assert case.deleted_at is None

    def test_case_str_representation(self):
        """Test string representation of Case"""
        case = Case(user_id=uuid4(), name="Test Case", partner_name="John")

        assert f"<Case(id={case.id}, name=Test Case)>" == str(case)

    def test_get_display_info(self):
        """Test get_display_info method"""
        case = Case(
            user_id=uuid4(), name="Meeting", partner_name="Bob", partner_type="client"
        )

        info = case.get_display_info()
        assert info["name"] == "Meeting"
        assert info["partner"] == "Bob"
        assert info["type"] == "client"
        assert "created_at" in info

    def test_set_metadata(self):
        """Test set_metadata method"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Test Partner")

        case.set_metadata("key1", "value1")
        assert case.case_metadata["key1"] == "value1"

        case.set_metadata("key2", {"nested": "data"})
        assert case.case_metadata["key2"] == {"nested": "data"}

    def test_get_metadata(self):
        """Test get_metadata method"""
        case = Case(
            user_id=uuid4(),
            name="Test",
            partner_name="Test Partner",
            case_metadata={"existing": "value", "number": 42},
        )

        assert case.get_metadata("existing") == "value"
        assert case.get_metadata("number") == 42
        assert case.get_metadata("nonexistent") is None
        assert case.get_metadata("nonexistent", "default") == "default"

    def test_is_deleted_property(self):
        """Test is_deleted property"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Test Partner")

        assert not case.is_deleted

        case.soft_delete()
        assert case.is_deleted

    def test_soft_delete(self):
        """Test soft delete functionality"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Test Partner")

        assert case.deleted_at is None

        case.soft_delete()
        assert case.deleted_at is not None
        assert isinstance(case.deleted_at, datetime)

    def test_restore(self):
        """Test restore functionality"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Test Partner")

        case.soft_delete()
        assert case.deleted_at is not None

        case.restore()
        assert case.deleted_at is None

    def test_long_text_fields(self):
        """Test handling of long text in fields"""
        long_name = "A" * 100  # Within limit
        long_partner_name = "B" * 100  # Within limit
        long_partner_type = "C" * 50  # Within limit
        long_purpose = "D" * 1000  # Long text for purpose

        case = Case(
            user_id=uuid4(),
            name=long_name,
            partner_name=long_partner_name,
            partner_type=long_partner_type,
            conversation_purpose=long_purpose,
        )

        assert case.name == long_name
        assert case.partner_name == long_partner_name
        assert case.partner_type == long_partner_type
        assert case.conversation_purpose == long_purpose

    def test_complex_metadata(self):
        """Test complex metadata structures"""
        complex_metadata = {
            "tags": ["work", "urgent", "client"],
            "settings": {
                "notification": True,
                "priority": 1,
                "reminder": {"enabled": True, "hours": 24},
            },
            "history": [
                {"action": "created", "timestamp": "2025-01-01T00:00:00Z"},
                {"action": "updated", "timestamp": "2025-01-02T00:00:00Z"},
            ],
        }

        case = Case(
            user_id=uuid4(),
            name="Complex Test",
            partner_name="Partner",
            case_metadata=complex_metadata,
        )

        assert case.case_metadata == complex_metadata
        assert case.get_metadata("tags") == ["work", "urgent", "client"]
        assert case.get_metadata("settings")["priority"] == 1


class TestCaseModelValidation:
    """Test Case model validation and edge cases"""

    def test_empty_metadata_default(self):
        """Test that metadata defaults to empty dict"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Partner")

        assert case.case_metadata == {}
        assert isinstance(case.case_metadata, dict)

    def test_metadata_operations_on_empty(self):
        """Test metadata operations on empty metadata"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Partner")

        # Should work on empty metadata
        assert case.get_metadata("anything") is None

        case.set_metadata("first", "value")
        assert case.case_metadata == {"first": "value"}

    def test_none_values_handling(self):
        """Test handling of None values"""
        case = Case(
            user_id=uuid4(),
            name="Test",
            partner_name="Partner",
            partner_type=None,
            my_position=None,
            conversation_purpose=None,
        )

        assert case.partner_type is None
        assert case.my_position is None
        assert case.conversation_purpose is None

    def test_empty_string_values(self):
        """Test handling of empty string values"""
        case = Case(
            user_id=uuid4(),
            name="Test",
            partner_name="Partner",
            partner_type="",
            my_position="",
            conversation_purpose="",
        )

        assert case.partner_type == ""
        assert case.my_position == ""
        assert case.conversation_purpose == ""


class TestCaseModelEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_repeated_soft_delete(self):
        """Test multiple soft deletes don't override timestamp"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Partner")

        case.soft_delete()
        first_delete_time = case.deleted_at

        # Wait a tiny bit (in real test might need sleep)
        case.soft_delete()
        second_delete_time = case.deleted_at

        # Should be the same timestamp
        assert first_delete_time == second_delete_time

    def test_restore_non_deleted_case(self):
        """Test restoring a case that wasn't deleted"""
        case = Case(user_id=uuid4(), name="Test", partner_name="Partner")

        assert case.deleted_at is None
        case.restore()  # Should be safe
        assert case.deleted_at is None

    def test_metadata_overwrite(self):
        """Test overwriting metadata values"""
        case = Case(
            user_id=uuid4(),
            name="Test",
            partner_name="Partner",
            case_metadata={"key": "original"},
        )

        assert case.get_metadata("key") == "original"

        case.set_metadata("key", "updated")
        assert case.get_metadata("key") == "updated"

        case.set_metadata("key", None)
        assert case.get_metadata("key") is None
