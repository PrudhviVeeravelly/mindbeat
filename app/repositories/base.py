"""Base repository pattern implementation."""

from typing import Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel

# Define generic types for models
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class with default methods to Create, Read, Update, Delete (CRUD).
    
    Attributes:
        model: The SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize repository with model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Optional[ModelType]: Found record or None
        """
        raise NotImplementedError

    async def get_all(self) -> List[ModelType]:
        """Get all records.
        
        Returns:
            List[ModelType]: List of all records
        """
        raise NotImplementedError

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record.
        
        Args:
            obj_in: Schema for creating record
            
        Returns:
            ModelType: Created record
        """
        raise NotImplementedError

    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update a record.
        
        Args:
            id: Record ID
            obj_in: Schema for updating record
            
        Returns:
            Optional[ModelType]: Updated record or None
        """
        raise NotImplementedError

    async def delete(self, id: int) -> bool:
        """Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        raise NotImplementedError
