from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProductSummary(BaseModel):
    """Summary information for a product."""
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime 