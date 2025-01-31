from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    research_quotes: List[str] = []
    marketing_angles: List[str] = []
    ad_scripts: List[str] = []
    insights: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    research_quotes: Optional[List[str]] = None
    marketing_angles: Optional[List[str]] = None
    ad_scripts: Optional[List[str]] = None
    insights: Optional[List[str]] = None

class ProductRead(ProductBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Product(ProductRead):
    """
    Legacy schema for backward compatibility.
    Use ProductRead for new code.
    """
    class Config:
        from_attributes = True 
