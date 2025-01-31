from typing import Optional, List, Dict
from pydantic import BaseModel, UUID4
from datetime import datetime

class ProductSummary(BaseModel):
    id: UUID4
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProjectProductsSummary(BaseModel):
    products: List[ProductSummary]
    total_count: int

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]
    products_summary: ProjectProductsSummary

    class Config:
        from_attributes = True

class ProjectUpdate(ProjectBase):
    pass 
