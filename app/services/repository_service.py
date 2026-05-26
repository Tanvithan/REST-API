from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DuplicateResourceError, ResourceNotFoundError
from ..db.repository_dao import (
    create_repository,
    delete_repository,
    get_repository_by_external_id,
    get_repository_by_id,
    update_repository,
)
from .github_service import fetch_github_repository, map_github_response
from ..db.models import Repository


class RepositoryService:
    """Business logic for GitHub repository CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, identifier: str) -> Repository:
        """Create a new repository record from a GitHub identifier."""
        existing = await get_repository_by_external_id(self.session, identifier)
        if existing:
            raise DuplicateResourceError("Repository already exists.")

        raw_payload = await fetch_github_repository(identifier)
        return await create_repository(self.session, map_github_response(raw_payload))

    async def get(self, repo_id: int) -> Repository | None:
        return await get_repository_by_id(self.session, repo_id)

    async def refresh(self, repo_id: int) -> Repository:
        """Refresh the stored repository metadata from GitHub and update timestamps."""
        repo = await self.get(repo_id)
        if repo is None:
            raise ResourceNotFoundError("Repository not found.")

        raw = await fetch_github_repository(repo.external_id)
        data = map_github_response(raw)
        now = datetime.now(timezone.utc)
        data["fetched_at"] = now
        data["updated_at"] = now
        return await update_repository(self.session, repo, data)

    async def delete(self, repo_id: int) -> None:
        repo = await self.get(repo_id)
        if repo is None:
            raise ResourceNotFoundError("Repository not found.")
        await delete_repository(self.session, repo)
