from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import json
from models.user import User
from models.product import Product
from models.project import Project
from schemas.product import ProductCreate, ProductUpdate
from .project import ProjectService

class ProductService:
    def __init__(self):
        self.project_service = ProjectService()

    def get_product(self, db: Session, product_id: UUID, user: User) -> Product:
        product = db.query(Product).join(Product.project).filter(
            Product.id == product_id,
            Product.project.has(user_id=user.id)
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    def get_products(self, db: Session, project_id: UUID, user: User, skip: int = 0, limit: int = 100) -> List[Product]:
        # Verify project exists and belongs to user
        self.project_service.get_project(db, project_id, user)
        return db.query(Product).filter(
            Product.project_id == project_id
        ).offset(skip).limit(limit).all()

    def create_product(self, project_id: UUID, product: ProductCreate, user: User, db: Session) -> Product:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )

        # Create product
        db_product = Product(**product.dict(), project_id=project_id)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def update_product(self, product_id: UUID, product_update: ProductUpdate, user: User, db: Session) -> Product:
        product = self.get_product(db, product_id, user)
        for key, value in product_update.dict(exclude_unset=True).items():
            if key in ['research_quotes', 'marketing_angles', 'ad_scripts', 'insights']:
                value = json.dumps(value)
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, product_id: UUID, user: User, db: Session) -> None:
        product = self.get_product(db, product_id, user)
        db.delete(product)
        db.commit() 