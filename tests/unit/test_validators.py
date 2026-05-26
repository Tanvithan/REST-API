import pytest

from app.utils.github_parser import parse_github_repository_identifier
from app.utils.validators import validate_owner_repo_format


class TestParseGithubRepositoryIdentifier:
    """Tests for parse_github_repository_identifier function."""

    def test_parse_valid_identifier(self):
        """Should accept a plain owner/repo identifier."""
        result = parse_github_repository_identifier(
            url=None, identifier="tiangolo/fastapi"
        )
        assert result == "tiangolo/fastapi"

    def test_parse_valid_url(self):
        """Should correctly parse a valid GitHub URL."""
        result = parse_github_repository_identifier(
            url="https://github.com/encode/starlette", identifier=None
        )
        assert result == "encode/starlette"

    def test_parse_url_with_trailing_slash(self):
        """Should handle trailing slash in URL."""
        result = parse_github_repository_identifier(
            url="https://github.com/pallets/flask/", identifier=None
        )
        assert result == "pallets/flask"

    def test_raises_when_both_url_and_identifier_provided(self):
        """Should reject when both url and identifier are provided."""
        with pytest.raises(ValueError, match="Provide exactly one"):
            parse_github_repository_identifier(
                url="https://github.com/owner/repo", identifier="owner/repo"
            )

    def test_raises_when_neither_url_nor_identifier_provided(self):
        """Should reject when neither url nor identifier is provided."""
        with pytest.raises(ValueError, match="Provide exactly one"):
            parse_github_repository_identifier(url=None, identifier=None)

    def test_raises_on_non_github_domain(self):
        """Should reject URLs not pointing to github.com."""
        with pytest.raises(ValueError, match="URL must point to github.com"):
            parse_github_repository_identifier(
                url="https://gitlab.com/owner/repo", identifier=None
            )

    def test_raises_on_invalid_url_scheme(self):
        """Should reject URLs without http/https."""
        with pytest.raises(ValueError, match="URL must start with http"):
            parse_github_repository_identifier(
                url="ftp://github.com/owner/repo", identifier=None
            )

    def test_raises_when_url_missing_owner_repo(self):
        """Should reject GitHub URLs that don't contain owner and repo."""
        with pytest.raises(ValueError, match="must contain owner and repository"):
            parse_github_repository_identifier(
                url="https://github.com/owner", identifier=None
            )


class TestValidateOwnerRepoFormat:
    """Tests for validate_owner_repo_format function."""

    def test_valid_owner_repo_format(self):
        """Should accept valid owner/repo format."""
        result = validate_owner_repo_format("tiangolo/fastapi")
        assert result == "tiangolo/fastapi"

    def test_accepts_dots_underscores_hyphens(self):
        """Should accept special characters allowed in repo names."""
        result = validate_owner_repo_format("some-org/repo_name.v2")
        assert result == "some-org/repo_name.v2"

    def test_rejects_missing_slash(self):
        """Should reject identifiers without a slash."""
        with pytest.raises(ValueError, match="owner/repository"):
            validate_owner_repo_format("justareponame")

    def test_rejects_extra_path_segments(self):
        """Should reject paths with more than owner/repo."""
        with pytest.raises(ValueError, match="owner/repository"):
            validate_owner_repo_format("owner/repo/extra")

    def test_rejects_empty_parts(self):
        """Should reject empty owner or repo name."""
        with pytest.raises(ValueError, match="owner/repository"):
            validate_owner_repo_format("owner/")

    def test_rejects_invalid_characters(self):
        """Should reject characters not allowed in repo names."""
        with pytest.raises(ValueError, match="owner/repository"):
            validate_owner_repo_format("owner/repo name")  # space is invalid
