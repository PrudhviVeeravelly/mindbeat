"""Base service pattern implementation."""

from typing import Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel

from app.repositories.base import BaseRepository

# Define generic types
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with default business logic.
    
    This class implements the service layer pattern, handling business logic
    and coordinating between repositories and external services.
    
    Attributes:
        repository: Instance of repository for data access
    """

    def __init__(self, repository: Type[BaseRepository]):
        """Initialize service with repository.
        
        Args:
            repository: Repository instance for data access
        """
        self.repository = repository

    async def get(self, id: int) -> Optional[ModelType]:
        """Get an item by ID.
        
        Args:
            id: Item ID
            
        Returns:
            Optional[ModelType]: Found item or None
        """
        return await self.repository.get(id)

    async def get_all(self) -> List[ModelType]:
        """Get all items.
        
        Returns:
            List[ModelType]: List of all items
        """
        return await self.repository.get_all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new item.
        
        Args:
            obj_in: Schema for creating item
            
        Returns:
            ModelType: Created item
        """
        return await self.repository.create(obj_in)

    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update an item.
        
        Args:
            id: Item ID
            obj_in: Schema for updating item
            
        Returns:
            Optional[ModelType]: Updated item or None
        """
        return await self.repository.update(id, obj_in)

    async def delete(self, id: int) -> bool:
        """Delete an item.
        
        Args:
            id: Item ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        return await self.repository.delete(id)
