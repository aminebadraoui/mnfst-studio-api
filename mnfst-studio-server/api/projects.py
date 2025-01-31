from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from db.deps import get_db
from core.auth import get_current_user
from models.user import User
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, Project
from services.project import ProjectService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])
project_service = ProjectService()

@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project."""
    logger.info(f"Creating project with data: {project.dict()}")
    result = project_service.create_project(db, project, current_user)
    logger.info(f"Created project result: {result.__dict__}")
    return result

@router.get("", response_model=List[Project])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects for the current user."""
    logger.info(f"Getting projects for user {current_user.id} with skip={skip}, limit={limit}")
    projects = project_service.get_projects(db, current_user, skip, limit)
    logger.info(f"Found {len(projects)} projects")
    for project in projects:
        logger.info(f"Project data: {project.__dict__}")
    return projects

@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project by ID."""
    logger.info(f"Getting project {project_id} for user {current_user.id}")
    result = project_service.get_project(db, project_id, current_user)
    logger.info(f"Project result: {result.__dict__}")
    return result

@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project."""
    logger.info(f"Updating project {project_id} with data: {project_update.dict()}")
    result = project_service.update_project(db, project_id, project_update, current_user)
    logger.info(f"Updated project result: {result.__dict__}")
    return result

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project."""
    logger.info(f"Deleting project {project_id}")
    project_service.delete_project(db, project_id, current_user)
    logger.info(f"Project {project_id} deleted successfully")

@router.post("/{project_id}/rebuild-summary", response_model=Project)
def rebuild_project_summary(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rebuild the products summary for a project."""
    logger.info(f"Rebuilding summary for project {project_id}")
    # First verify the project exists and user has access
    project = project_service.get_project(db, project_id, current_user)
    # Rebuild the summary
    project_service.rebuild_products_summary(db, project_id)
    # Fetch and return the updated project
    result = project_service.get_project(db, project_id, current_user)
    logger.info(f"Rebuilt project summary result: {result.__dict__}")
    return result 
