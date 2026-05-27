from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db_session
from ..schemas.repository import RepositoryCreate, RepositoryRead
from ..services.repository_service import RepositoryService

router = APIRouter(prefix="/repos", tags=["repositories"])


@router.post("/", response_model=RepositoryRead, status_code=201)
async def create_repo(payload: RepositoryCreate, session: AsyncSession = Depends(get_db_session)) -> RepositoryRead:
    """Create a new repository record from a GitHub identifier or URL."""
    service = RepositoryService(session)
    return await service.create(payload.identifier)


@router.get("/{repo_id}", response_model=RepositoryRead)
async def get_repo(repo_id: int, session: AsyncSession = Depends(get_db_session)) -> RepositoryRead:
    """Retrieve a stored repository by local database ID."""
    service = RepositoryService(session)
    repo = await service.get(repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo


@router.put("/{repo_id}", response_model=RepositoryRead)
async def refresh_repo(repo_id: int, session: AsyncSession = Depends(get_db_session)) -> RepositoryRead:
    """Refresh an existing repository from GitHub and persist the latest metadata."""
    service = RepositoryService(session)
    return await service.refresh(repo_id)


@router.delete("/{repo_id}", status_code=204)
async def delete_repo(repo_id: int, session: AsyncSession = Depends(get_db_session)) -> Response:
    """Delete a stored repository by ID."""
    service = RepositoryService(session)
    await service.delete(repo_id)
    return Response(status_code=204)
