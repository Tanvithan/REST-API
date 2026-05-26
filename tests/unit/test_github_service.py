import pytest
from app.services.github_service import map_github_response


def test_map_github_response_full_data():
    """Test mapping with a complete GitHub response."""
    github_response = {
        "full_name": "encode/starlette",
        "owner": {"login": "encode"},
        "name": "starlette",
        "description": "The little ASGI framework that shines.",
        "html_url": "https://github.com/encode/starlette",
        "stargazers_count": 8500,
        "forks_count": 650,
        "open_issues_count": 45,
        "language": "Python",
        "id": 123456,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjM0NTY=",
    }

    result = map_github_response(github_response)

    assert result["external_id"] == "encode/starlette"
    assert result["full_name"] == "encode/starlette"
    assert result["owner"] == "encode"
    assert result["name"] == "starlette"
    assert result["description"] == "The little ASGI framework that shines."
    assert result["html_url"] == "https://github.com/encode/starlette"
    assert result["stargazers_count"] == 8500
    assert result["forks_count"] == 650
    assert result["open_issues_count"] == 45
    assert result["language"] == "Python"
    assert result["raw_data"] == github_response


def test_map_github_response_minimal_data():
    """Test mapping when optional fields are missing."""
    github_response = {
        "full_name": "tiangolo/fastapi",
        "owner": {"login": "tiangolo"},
        "name": "fastapi",
        "html_url": "https://github.com/tiangolo/fastapi",
    }

    result = map_github_response(github_response)

    assert result["external_id"] == "tiangolo/fastapi"
    assert result["description"] is None
    assert result["language"] is None
    assert result["stargazers_count"] == 0
    assert result["forks_count"] == 0
    assert result["open_issues_count"] == 0


def test_map_github_response_preserves_raw_data():
    """Ensure the entire original GitHub payload is stored in raw_data."""
    github_response = {
        "full_name": "pallets/flask",
        "owner": {"login": "pallets"},
        "name": "flask",
        "html_url": "https://github.com/pallets/flask",
        "extra_field": "should be preserved",
    }

    result = map_github_response(github_response)

    assert result["raw_data"] == github_response
    assert result["raw_data"]["extra_field"] == "should be preserved"
