"""Database access functions for GitHub repository records."""

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DuplicateResourceError, ResourceNotFoundError
from .models import Repository


async def get_repository_by_id(session: AsyncSession, repo_id: int) -> Repository | None:
    """Return a repository record by primary key."""
    result = await session.execute(select(Repository).where(Repository.id == repo_id))
    return result.scalars().first()


async def get_repository_by_external_id(session: AsyncSession, external_id: str) -> Repository | None:
    result = await session.execute(select(Repository).where(Repository.external_id == external_id))
    return result.scalars().first()


async def create_repository(session: AsyncSession, payload: dict) -> Repository:
    repo = Repository(**payload)
    session.add(repo)
    try:
        await session.commit()
        await session.refresh(repo)
        return repo
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateResourceError("Repository already exists.") from exc


async def update_repository(session: AsyncSession, repo: Repository, payload: dict) -> Repository:
    result = await session.execute(
        update(Repository)
        .where(Repository.id == repo.id)
        .values(**payload)
    )
    if result.rowcount == 0:
        await session.rollback()
        raise ResourceNotFoundError("Repository disappeared during update.")

    await session.commit()
    await session.refresh(repo)
    return repo


async def delete_repository(session: AsyncSession, repo: Repository) -> None:
    await session.execute(delete(Repository).where(Repository.id == repo.id))
    await session.commit()
