import pytest
from unittest.mock import patch, AsyncMock

from app.services.repository_service import fetch_github_repository, map_github_response


# Raw response that fetch_github_repository would return (as if from GitHub API)
RAW_GITHUB_RESPONSE = {
    "full_name": "encode/starlette",
    "owner": {"login": "encode"},
    "name": "starlette",
    "description": "The little ASGI framework that shines.",
    "html_url": "https://github.com/encode/starlette",
    "stargazers_count": 8500,
    "forks_count": 620,
    "open_issues_count": 38,
    "language": "Python",
    "id": 123456,
    "node_id": "MDEwOlJlcG9zaXRvcnkxMjM0NTY=",
}

# What map_github_response should return (flat dict that the Repository model expects)
MAPPED_DATA = {
    "external_id": "encode/starlette",
    "full_name": "encode/starlette",
    "owner": "encode",
    "name": "starlette",
    "description": "The little ASGI framework that shines.",
    "html_url": "https://github.com/encode/starlette",
    "stargazers_count": 8500,
    "forks_count": 620,
    "open_issues_count": 38,
    "language": "Python",
    "raw_data": RAW_GITHUB_RESPONSE,
}


@pytest.mark.asyncio
class TestRepositoryAPIIntegration:
    """Integration tests for the four CRUD endpoints (as required by the assignment)."""

    async def test_post_create_success_returns_201(self, client):
        """POST should return 201 Created when a new repository is created."""
        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=RAW_GITHUB_RESPONSE,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=MAPPED_DATA,
        ):
            response = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "encode/starlette"
        assert data["owner"] == "encode"

    async def test_post_duplicate_returns_409(self, client):
        """POST should return 409 Conflict when trying to create a duplicate repository."""
        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=RAW_GITHUB_RESPONSE,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=MAPPED_DATA,
        ):
            # First creation
            await client.post("/repos/", json={"identifier": "encode/starlette"})

            # Second creation (duplicate)
            response = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    async def test_post_invalid_input_returns_422(self, client):
        """POST should return 422 when input validation fails."""
        # Missing both url and identifier
        response = await client.post("/repos/", json={})

        assert response.status_code == 422

        # Invalid format
        response = await client.post("/repos/", json={"identifier": "not-a-valid-repo"})
        assert response.status_code == 422

    async def test_get_existing_returns_200(self, client):
        """GET /repos/{id} should return 200 when the repository exists."""
        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=RAW_GITHUB_RESPONSE,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=MAPPED_DATA,
        ):
            create_resp = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )
            repo_id = create_resp.json()["id"]

            response = await client.get(f"/repos/{repo_id}")

        assert response.status_code == 200
        assert response.json()["id"] == repo_id

    async def test_get_non_existent_returns_404(self, client):
        """GET /repos/{id} should return 404 when the repository does not exist."""
        response = await client.get("/repos/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_put_refresh_existing_returns_200(self, client):
        """PUT /repos/{id} should refresh the repository and return 200."""
        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=RAW_GITHUB_RESPONSE,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=MAPPED_DATA,
        ):
            create_resp = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )
            repo_id = create_resp.json()["id"]

            response = await client.put(f"/repos/{repo_id}")

        assert response.status_code == 200
        assert response.json()["id"] == repo_id

    async def test_put_refresh_persists_updated_fields(self, client):
        """PUT /repos/{id} should persist updated repository fields in the DB."""
        changed_data = RAW_GITHUB_RESPONSE.copy()
        changed_data["description"] = "Updated description"
        changed_mapped_data = MAPPED_DATA.copy()
        changed_mapped_data["description"] = "Updated description"

        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=changed_data,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=changed_mapped_data,
        ):
            create_resp = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )
            repo_id = create_resp.json()["id"]

            response = await client.put(f"/repos/{repo_id}")

        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    async def test_put_non_existent_returns_404(self, client):
        """PUT /repos/{id} should return 404 when trying to refresh a non-existent repo."""
        response = await client.put("/repos/99999")
        assert response.status_code == 404

    async def test_delete_existing_returns_204(self, client):
        """DELETE /repos/{id} should return 204 No Content on success."""
        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            return_value=RAW_GITHUB_RESPONSE,
        ), patch(
            "app.services.repository_service.map_github_response",
            return_value=MAPPED_DATA,
        ):
            create_resp = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )
            repo_id = create_resp.json()["id"]

            response = await client.delete(f"/repos/{repo_id}")

        assert response.status_code == 204

    async def test_delete_non_existent_returns_404(self, client):
        """DELETE /repos/{id} should return 404 when trying to delete a non-existent repo."""
        response = await client.delete("/repos/99999")
        assert response.status_code == 404

    async def test_post_external_service_unavailable_returns_503(self, client):
        """POST should return 503 when the GitHub API cannot be reached."""
        from app.core.exceptions import ExternalServiceUnavailableError

        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            side_effect=ExternalServiceUnavailableError("GitHub API unavailable."),
        ):
            response = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )

        assert response.status_code == 503

    async def test_post_external_api_error_returns_502(self, client):
        """POST should return 502 when GitHub returns a non-404 error."""
        from app.core.exceptions import ExternalAPIError

        with patch(
            "app.services.repository_service.fetch_github_repository",
            new_callable=AsyncMock,
            side_effect=ExternalAPIError("GitHub API error."),
        ):
            response = await client.post(
                "/repos/", json={"identifier": "encode/starlette"}
            )

        assert response.status_code == 502
