from pydantic import BaseModel
from typing import List
from .product_summary import ProductSummary

class ProjectProductsSummary(BaseModel):
    """Summary information for all products in a project."""
    total_count: int
    products: List[ProductSummary] 
