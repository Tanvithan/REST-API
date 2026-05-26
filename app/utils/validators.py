import re


def validate_owner_repo_format(value: str) -> str:
    """Ensure the GitHub identifier is in owner/repository format."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Identifier must be in the format owner/repository.")
    return value
