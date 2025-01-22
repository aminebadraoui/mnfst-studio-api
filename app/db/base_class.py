from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, registry

mapper_registry = registry()

__all__ = ['Base']

class Base(DeclarativeBase):
    id: Any
    __name__: str
    registry = mapper_registry
    
    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 