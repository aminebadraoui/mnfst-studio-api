from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from db.deps import get_db
from core.auth import get_current_user
from models.user import User
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate, Product
from services.product import ProductService
from services.project import ProjectService

# Changed from /products to empty string since we're using full paths in routes
router = APIRouter(tags=["products"])
product_service = ProductService()
project_service = ProjectService()

@router.post("/projects/{project_id}/products", response_model=Product)
def create_product(
    project_id: UUID,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.create_product(project_id, product, current_user, db)

@router.get("/projects/{project_id}/products", response_model=List[Product])
def get_products(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.get_products(db, project_id, current_user)

@router.get("/projects/{project_id}/products/{product_id}", response_model=Product)
def get_product(
    project_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product by ID."""
    return product_service.get_product(db, product_id, current_user)

@router.put("/projects/{project_id}/products/{product_id}", response_model=Product)
def update_product(
    project_id: UUID,
    product_id: UUID,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product."""
    return product_service.update_product(db, product_id, product_update, current_user)

@router.delete("/projects/{project_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    project_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product."""
    product_service.delete_product(db, product_id, current_user)
    return {"message": "Product deleted successfully"} 
