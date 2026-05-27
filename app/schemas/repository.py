from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, model_validator

from ..utils.github_parser import parse_github_repository_identifier
from ..utils.validators import validate_owner_repo_format


class RepositoryCreate(BaseModel):
    """Input model for creating a new repository record."""
    url: Optional[AnyUrl] = Field(None, description="GitHub repository URL")
    identifier: Optional[str] = Field(None, description="GitHub owner/repository identifier")

    @model_validator(mode="before")
    @classmethod
    def validate_input(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize URL input into owner/repo before the route handler runs."""
        values["identifier"] = parse_github_repository_identifier(
            values.get("url"), values.get("identifier")
        )
        values["identifier"] = validate_owner_repo_format(values["identifier"])
        return values


class RepositoryRead(BaseModel):
    id: int
    external_id: str
    full_name: str
    owner: str
    name: str
    description: Optional[str]
    html_url: str
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    language: Optional[str]
    raw_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)
