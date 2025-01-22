from ..db.base_class import Base
from .user import User  # This ensures all models are imported for Alembic

__all__ = ['Base', 'User'] 