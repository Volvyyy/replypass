"""
Base repository class for common CRUD operations
"""

from typing import Type, TypeVar, Generic, Optional, List, Any, Dict
from uuid import UUID

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class with common CRUD operations
    
    Following SQLAlchemy 2.0 async best practices
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository with model class and async session
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record
        
        Args:
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Get record by ID
        
        Args:
            id: Record UUID
            
        Returns:
            Model instance or None if not found
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Get record by specific field
        
        Args:
            field_name: Name of the field
            value: Field value to search for
            
        Returns:
            Model instance or None if not found
        """
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = "created_at",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        List records with pagination and filtering
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Field name to order by
            filters: Dictionary of field filters
            
        Returns:
            List of model instances
        """
        stmt = select(self.model)
        
        # Apply filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    stmt = stmt.where(field == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            stmt = stmt.order_by(order_field.desc())
        
        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID
        
        Args:
            id: Record UUID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        from datetime import datetime
        
        # First check if record exists
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        # Update fields
        for field_name, value in kwargs.items():
            if hasattr(instance, field_name):
                setattr(instance, field_name, value)
        
        # Always update the updated_at timestamp
        if hasattr(instance, 'updated_at'):
            setattr(instance, 'updated_at', datetime.utcnow())
        
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record UUID
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of records
        """
        stmt = select(func.count(self.model.id))
        
        # Apply filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    stmt = stmt.where(field == value)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def exists(self, id: UUID) -> bool:
        """
        Check if record exists by ID
        
        Args:
            id: Record UUID
            
        Returns:
            True if exists, False otherwise
        """
        stmt = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0