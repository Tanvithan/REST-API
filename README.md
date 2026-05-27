# GitHub Repository Bridge API

A FastAPI service that stores GitHub repository metadata in PostgreSQL.

## Project overview

This service accepts a GitHub repository URL or `owner/repository` identifier, fetches metadata from the GitHub REST API, and stores the result in a local PostgreSQL database. I chose GitHub because it has stable JSON responses, clear repository identifiers, and optional token authentication for higher rate limits.

## Architecture summary

The application uses a layered structure:

- **API layer**: `app/api/repository_routes.py` defines the HTTP routes and status codes.
- **Schema layer**: `app/schemas/repository.py` validates request bodies before service logic runs.
- **Service layer**: `app/services/` contains business logic and GitHub API integration.
- **Data layer**: `app/db/` contains the async SQLAlchemy setup, ORM model, and database access functions.

For `POST /repos/`, FastAPI validates the body with `RepositoryCreate`, the service checks for duplicates, GitHub metadata is fetched with `httpx.AsyncClient`, the response is mapped into the ORM shape, and the record is committed to PostgreSQL.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Git

## Setup instructions

1. Clone the repository:

```bash
git clone <your-repo-url>
cd RestApi
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update the values:

```bash
copy .env.example .env
```

5. Create a PostgreSQL database, for example `github_bridge`.

6. Initialize the database schema:

```bash
python -m app.init_db
```

7. Start the API server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | None | Async SQLAlchemy PostgreSQL connection string. |
| `GITHUB_TOKEN` | No | Empty | Optional GitHub token used for higher API rate limits. |
| `EXTERNAL_API_TIMEOUT` | No | `10` | Timeout in seconds for GitHub API requests. |
| `GITHUB_API_BASE` | No | `https://api.github.com` | Base URL for the GitHub API. |

## API reference

### POST /repos/

Creates a new stored repository record from GitHub.

Request body with identifier:

```json
{
  "identifier": "encode/starlette"
}
```

Request body with URL:

```json
{
  "url": "https://github.com/encode/starlette"
}
```

`201 Created`

```json
{
  "id": 1,
  "external_id": "encode/starlette",
  "full_name": "encode/starlette",
  "owner": "encode",
  "name": "starlette",
  "description": "The little ASGI framework that shines.",
  "html_url": "https://github.com/encode/starlette",
  "stargazers_count": 8500,
  "forks_count": 650,
  "open_issues_count": 45,
  "language": "Python",
  "raw_data": {},
  "created_at": "2026-05-01T12:00:00+00:00",
  "updated_at": "2026-05-01T12:00:00+00:00",
  "fetched_at": "2026-05-01T12:00:00+00:00"
}
```

`409 Conflict`

```json
{
  "detail": "Repository already exists."
}
```

`422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, Identifier must be in the format owner/repository."
    }
  ]
}
```

`404 Not Found`

```json
{
  "detail": "Repository not found on GitHub."
}
```

`502 Bad Gateway`

```json
{
  "detail": "GitHub API returned status 500."
}
```

`503 Service Unavailable`

```json
{
  "detail": "Unable to reach GitHub API."
}
```

### GET /repos/{id}

Retrieves a stored repository by local database ID. This endpoint reads only from the local database.

`200 OK`

```json
{
  "id": 1,
  "external_id": "encode/starlette",
  "full_name": "encode/starlette",
  "owner": "encode",
  "name": "starlette",
  "description": "The little ASGI framework that shines.",
  "html_url": "https://github.com/encode/starlette",
  "stargazers_count": 8500,
  "forks_count": 650,
  "open_issues_count": 45,
  "language": "Python",
  "raw_data": {},
  "created_at": "2026-05-01T12:00:00+00:00",
  "updated_at": "2026-05-01T12:00:00+00:00",
  "fetched_at": "2026-05-01T12:00:00+00:00"
}
```

`404 Not Found`

```json
{
  "detail": "Repository not found."
}
```

### PUT /repos/{id}

Refreshes an existing stored repository by re-fetching metadata from GitHub.

`200 OK`

```json
{
  "id": 1,
  "external_id": "encode/starlette",
  "full_name": "encode/starlette",
  "owner": "encode",
  "name": "starlette",
  "description": "Updated repository description",
  "html_url": "https://github.com/encode/starlette",
  "stargazers_count": 9000,
  "forks_count": 700,
  "open_issues_count": 50,
  "language": "Python",
  "raw_data": {},
  "created_at": "2026-05-01T12:00:00+00:00",
  "updated_at": "2026-05-01T13:00:00+00:00",
  "fetched_at": "2026-05-01T13:00:00+00:00"
}
```

`404 Not Found`

```json
{
  "detail": "Repository not found."
}
```

If the local record exists but GitHub no longer has the repository:

```json
{
  "detail": "Repository not found on GitHub."
}
```

`502 Bad Gateway`

```json
{
  "detail": "GitHub API returned status 500."
}
```

`503 Service Unavailable`

```json
{
  "detail": "GitHub API request timed out."
}
```

### DELETE /repos/{id}

Deletes a stored repository by local database ID.

`204 No Content`

The response body is empty.

`404 Not Found`

```json
{
  "detail": "Repository not found."
}
```

## Running the tests

Run all tests:

```bash
python -m pytest
```

On Windows, if `pytest` is not on your PATH:

```bash
.venv\Scripts\python -m pytest
```

Run unit tests only:

```bash
python -m pytest tests/unit/
```

Run integration tests only:

```bash
python -m pytest tests/integration/
```

The unit tests cover input parsing, validation, GitHub response mapping, and duplicate detection logic. The integration tests cover all four endpoints, required success/error cases, and bonus external API failure responses.

## Design decisions

- Used GitHub repositories as the external resource because `owner/repo` identifiers are simple to validate before making network calls.
- Used `httpx.AsyncClient` so external API calls stay non-blocking inside async FastAPI endpoints.
- Enforced duplicate protection with a database-level unique constraint on `external_id`, while also checking early in the service layer for a clearer `409 Conflict` response.
- Stored selected metadata columns for easy querying and kept `raw_data` so the full upstream response is still available.
- Used a lightweight ORM initialization script instead of Alembic to keep the local setup simple for this assessment.

## Assumptions

- The service supports GitHub repositories only, not users, organizations, gists, or issues.
- `POST /repos/` accepts exactly one of `url` or `identifier`.
- A GitHub repository URL is normalized to `owner/repository`; extra path segments after the repository name are ignored.
- `GITHUB_TOKEN` is optional because public GitHub repository metadata can be fetched without authentication, but rate limits are lower without a token.

## Troubleshooting

- `Database connection failed`: verify `DATABASE_URL`, confirm PostgreSQL is running, and make sure the database exists.
- `ModuleNotFoundError`: activate the virtual environment and run `python -m pip install -r requirements.txt`.
- `422 Unprocessable Entity`: send exactly one of `url` or `identifier`, and use the `owner/repository` format for identifiers.
- `409 Conflict`: the same GitHub repository is already stored; use `GET`, `PUT`, or `DELETE` with the existing record ID.
- `503 Service Unavailable`: GitHub may be unreachable, DNS may be failing, or the configured timeout may be too low.

## Notes

- `.env.example` lists the required configuration variables with placeholder values.
- `.env`, virtual environments, Python cache files, and logs are excluded by `.gitignore`.
- Docker support is not included; this project uses local PostgreSQL plus the database initialization script.
