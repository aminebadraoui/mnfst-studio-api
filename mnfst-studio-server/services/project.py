from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from models.user import User
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def get_project(db: Session, project_id: UUID, user: User) -> Project:
        logger.info(f"Fetching project {project_id} for user {user.id}")
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user.id
        ).first()
        if not project:
            logger.warning(f"Project {project_id} not found for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        logger.info(f"Project data: {project.__dict__}")
        return project

    @staticmethod
    def get_projects(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Project]:
        logger.info(f"Fetching projects for user {user.id} with skip={skip}, limit={limit}")
        projects = db.query(Project).filter(
            Project.user_id == user.id
        ).offset(skip).limit(limit).all()
        logger.info(f"Found {len(projects)} projects")
        for project in projects:
            logger.info(f"Project data: {project.__dict__}")
        return projects

    @staticmethod
    def create_project(db: Session, project: ProjectCreate, user: User) -> Project:
        logger.info(f"Creating new project for user {user.id}")
        db_project = Project(**project.dict(), user_id=user.id)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        logger.info(f"Created project: {db_project.__dict__}")
        return db_project

    def update_project(self, db: Session, project_id: UUID, project_update: ProjectUpdate, user: User) -> Project:
        logger.info(f"Updating project {project_id} for user {user.id}")
        db_project = self.get_project(db, project_id, user)
        for field, value in project_update.dict(exclude_unset=True).items():
            setattr(db_project, field, value)
        db.commit()
        db.refresh(db_project)
        logger.info(f"Updated project: {db_project.__dict__}")
        return db_project

    def delete_project(self, db: Session, project_id: UUID, user: User) -> None:
        logger.info(f"Deleting project {project_id} for user {user.id}")
        db_project = self.get_project(db, project_id, user)
        db.delete(db_project)
        db.commit()
        logger.info(f"Project {project_id} deleted successfully")

    @staticmethod
    def rebuild_products_summary(db: Session, project_id: UUID) -> None:
        logger.info(f"Rebuilding products summary for project {project_id}")
        try:
            db.execute(
                text('SELECT rebuild_project_products_summary(:project_id)'),
                {'project_id': project_id}
            )
            db.commit()
            logger.info("Products summary rebuilt successfully")
        except Exception as e:
            logger.error(f"Error rebuilding products summary: {str(e)}")
            raise 