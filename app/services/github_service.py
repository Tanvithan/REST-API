"""GitHub external API integration helpers."""

import httpx

from ..core.config import settings
from ..core.exceptions import ExternalAPIError, ExternalServiceUnavailableError, ResourceNotFoundError


def map_github_response(payload: dict) -> dict:
    """Convert raw GitHub JSON into internal repository fields."""
    if not isinstance(payload, dict):
        raise ExternalAPIError(f"GitHub returned non-object response (type={type(payload).__name__})")

    if "full_name" not in payload or "owner" not in payload:
        keys = list(payload.keys())[:15] if isinstance(payload, dict) else []
        raise ExternalAPIError(
            f"GitHub response missing required fields. "
            f"Top-level keys: {keys}. "
            f"Message: {payload.get('message')}"
        )

    owner = payload.get("owner") or {}
    return {
        "external_id": payload["full_name"],
        "full_name": payload["full_name"],
        "owner": owner.get("login"),
        "name": payload.get("name"),
        "description": payload.get("description"),
        "html_url": payload.get("html_url"),
        "stargazers_count": payload.get("stargazers_count", 0),
        "forks_count": payload.get("forks_count", 0),
        "open_issues_count": payload.get("open_issues_count", 0),
        "language": payload.get("language"),
        "raw_data": payload,
    }


async def fetch_github_repository(identifier: str) -> dict:
    """Fetch repository metadata from GitHub using the configured base URL and token."""
    url = f"{settings.github_api_base}/repos/{identifier}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    timeout = httpx.Timeout(settings.external_api_timeout, connect=settings.external_api_timeout)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
        except httpx.ReadTimeout as exc:
            raise ExternalServiceUnavailableError("GitHub API request timed out.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceUnavailableError("Unable to reach GitHub API.") from exc

    if response.status_code == 404:
        raise ResourceNotFoundError("Repository not found on GitHub.")
    if response.status_code >= 400:
        raise ExternalAPIError(f"GitHub API returned status {response.status_code}.")

    return response.json()
