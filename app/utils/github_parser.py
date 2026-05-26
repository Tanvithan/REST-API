from urllib.parse import urlparse
from typing import Optional


def parse_github_repository_identifier(url: Optional[str] = None, identifier: Optional[str] = None) -> str:
    """Normalize a GitHub URL or owner/repo identifier into owner/repo form."""
    if bool(url) == bool(identifier):
        raise ValueError("Provide exactly one of 'url' or 'identifier'.")

    if url:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("URL must start with http:// or https://.")
        if parsed.netloc.lower() != "github.com":
            raise ValueError("URL must point to github.com.")
        parts = [segment for segment in parsed.path.split("/") if segment]
        if len(parts) < 2:
            raise ValueError("GitHub URL must contain owner and repository name.")
        return f"{parts[0]}/{parts[1]}"

    return identifier.strip()
