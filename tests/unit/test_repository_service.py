import pytest
from unittest.mock import AsyncMock, patch

from app.services.repository_service import RepositoryService
from app.core.exceptions import DuplicateResourceError, ResourceNotFoundError
from app.db.models import Repository


@pytest.mark.asyncio
class TestRepositoryServiceDuplicateLogic:
    """Unit tests focusing on duplicate detection logic in RepositoryService."""

    async def test_create_raises_duplicate_when_repo_already_exists(self):
        """Should raise DuplicateResourceError if a repo with the same external_id exists."""
        # Arrange
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        existing_repo = Repository(id=1, external_id="tiangolo/fastapi")
        
        with patch(
            "app.services.repository_service.get_repository_by_external_id",
            new_callable=AsyncMock,
            return_value=existing_repo,
        ):
            # Act & Assert
            with pytest.raises(DuplicateResourceError, match="Repository already exists"):
                await service.create("tiangolo/fastapi")

    async def test_create_succeeds_when_repo_does_not_exist(self):
        """Should fetch from GitHub and create the repo when it doesn't exist."""
        # Arrange
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        fake_github_data = {"full_name": "tiangolo/fastapi", "owner": {"login": "tiangolo"}}
        fake_mapped_data = {"full_name": "tiangolo/fastapi", "owner": "tiangolo"}
        created_repo = Repository(id=42, external_id="tiangolo/fastapi")

        with patch(
            "app.services.repository_service.get_repository_by_external_id",
            new_callable=AsyncMock,
            return_value=None,  # No existing repo
        ), patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=fake_github_data,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=fake_mapped_data,
        ), patch(
            "app.services.repository_service.create_repository",
            new_callable=AsyncMock,
            return_value=created_repo,
        ) as mock_create:
            # Act
            result = await service.create("tiangolo/fastapi")

            # Assert
            assert result.id == 42
            mock_create.assert_awaited_once_with(mock_session, fake_mapped_data)


@pytest.mark.asyncio
class TestRepositoryServiceOtherMethods:
    """Additional unit tests for other service methods."""

    async def test_get_returns_repo_when_found(self):
        """Should return the repository when it exists."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)
        expected_repo = Repository(id=5, external_id="some/repo")

        with patch(
            "app.services.repository_service.get_repository_by_id",
            new_callable=AsyncMock,
            return_value=expected_repo,
        ):
            result = await service.get(5)
            assert result == expected_repo

    async def test_get_returns_none_when_not_found(self):
        """Should return None when repository does not exist."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        with patch(
            "app.services.repository_service.get_repository_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await service.get(999)
            assert result is None

    async def test_refresh_raises_not_found_when_repo_missing(self):
        """Should raise ResourceNotFoundError when trying to refresh a non-existent repo."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        with patch.object(service, "get", new_callable=AsyncMock, return_value=None):
            with pytest.raises(ResourceNotFoundError, match="Repository not found"):
                await service.refresh(123)

    async def test_delete_raises_not_found_when_repo_missing(self):
        """Should raise ResourceNotFoundError when trying to delete a non-existent repo."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        with patch.object(service, "get", new_callable=AsyncMock, return_value=None):
            with pytest.raises(ResourceNotFoundError, match="Repository not found"):
                await service.delete(123)


@pytest.mark.asyncio
class TestRepositoryServiceRefreshAndDelete:
    """Deeper tests for refresh and delete logic."""

    async def test_refresh_successfully_updates_repo(self):
        """Should fetch fresh data from GitHub and update the repository with new timestamps."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)

        existing_repo = Repository(id=7, external_id="encode/starlette")
        fresh_github_data = {"full_name": "encode/starlette", "stargazers_count": 12000}
        mapped_data = {"full_name": "encode/starlette", "stargazers_count": 12000}

        with patch.object(service, "get", new_callable=AsyncMock, return_value=existing_repo), \
             patch(
                 "app.services.repository_service.fetch_github_repository",
                 new_callable=AsyncMock,
                 return_value=fresh_github_data,
             ), \
             patch(
                 "app.services.repository_service.map_github_response",
                 return_value=mapped_data,
             ), \
             patch(
                 "app.services.repository_service.update_repository",
                 new_callable=AsyncMock,
             ) as mock_update:

            result = await service.refresh(7)

            assert result is not None
            mock_update.assert_awaited_once()
            # Verify that fetched_at and updated_at were added
            call_args = mock_update.call_args[0][2]
            assert "fetched_at" in call_args
            assert "updated_at" in call_args

    async def test_delete_successfully_deletes_existing_repo(self):
        """Should successfully delete a repository that exists."""
        mock_session = AsyncMock()
        service = RepositoryService(mock_session)
        existing_repo = Repository(id=9, external_id="some/repo")

        with patch.object(service, "get", new_callable=AsyncMock, return_value=existing_repo), \
             patch(
                 "app.services.repository_service.delete_repository",
                 new_callable=AsyncMock,
             ) as mock_delete:

            await service.delete(9)

            mock_delete.assert_awaited_once_with(mock_session, existing_repo)
