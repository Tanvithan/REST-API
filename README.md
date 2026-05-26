<<<<<<< HEAD
# GitHub Repository Bridge API

A simple FastAPI service that stores GitHub repository metadata in PostgreSQL.

## Project overview

This service accepts a GitHub repository URL or `owner/repository` identifier, fetches repository metadata from GitHub, and stores it in a local PostgreSQL database. It provides CRUD operations for stored entries and keeps the data fresh with a refresh endpoint.

## Architecture summary

The code is split into clear layers:

- **API layer**: `app/api/repository_routes.py` defines the HTTP routes.
- **Service layer**: `app/services/` contains business logic and GitHub API integration.
- **Data layer**: `app/db/` handles the async SQLAlchemy database connection, ORM model, and database operations.
- **Schema layer**: `app/schemas/repository.py` validates input and serializes response data.

When a client sends `POST /repos/`, the request is validated, GitHub data is fetched, mapped into the internal model, saved to the database, and returned as JSON.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- `git`

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
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update the values:

```bash
copy .env.example .env
```

5. Create a PostgreSQL database and set its URL in `.env`.

6. Initialize the database schema:

```bash
python -m app.init_db
```

7. Start the API server:

```bash
uvicorn app.main:app --reload
```

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | yes | none | PostgreSQL connection string | 
| `GITHUB_TOKEN` | no | empty | Optional GitHub token for higher rate limits | 
| `EXTERNAL_API_TIMEOUT` | no | `10` | GitHub request timeout in seconds | 
| `GITHUB_API_BASE` | no | `https://api.github.com` | GitHub API base URL | 

## API reference

### POST /repos/

Create a new repository record.

Request body:

```json
{
  "identifier": "encode/starlette"
}
```

Or:

```json
{
  "url": "https://github.com/encode/starlette"
}
```

Responses:

- `201 Created`
- `409 Conflict` if the repository already exists
- `422 Unprocessable Entity` if input is invalid
- `502 Bad Gateway` if GitHub returns an unexpected error
- `503 Service Unavailable` if GitHub is unreachable or times out

Example response:

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
  "raw_data": { ... },
  "created_at": "2026-05-01T12:00:00+00:00",
  "updated_at": "2026-05-01T12:00:00+00:00",
  "fetched_at": "2026-05-01T12:00:00+00:00"
}
```

### GET /repos/{id}

Retrieve a stored repository by local database ID.

Responses:

- `200 OK` with the repository record
- `404 Not Found` if the ID does not exist

### PUT /repos/{id}

Refresh the stored repository metadata from GitHub.

Responses:

- `200 OK` with the updated record
- `404 Not Found` if the record does not exist
- `502 Bad Gateway` if GitHub returns an error
- `503 Service Unavailable` if GitHub is unreachable or times out

### DELETE /repos/{id}

Remove the stored repository.

Responses:

- `204 No Content` if deleted successfully
- `404 Not Found` if the record does not exist

## Running the tests

Run all tests:

```bash
pytest
```

Run unit tests only:

```bash
pytest tests/unit/
```

Run integration tests only:

```bash
pytest tests/integration/
```

## Design decisions

- Used the GitHub REST API for repository metadata because it is well-known, stable, and supports URL or `owner/repo` lookup.
- Used FastAPI with async SQLAlchemy for fully asynchronous request handling and clean separation of layers.
- Implemented centralized error handling with custom `ServiceError` exceptions and a single FastAPI exception handler.

## Assumptions

- This service stores only GitHub repositories, not users or other GitHub resource types.
- `POST /repos/` accepts either `url` or `identifier`, but not both.
- Database initialization is done through `python -m app.init_db` rather than a migration tool.

## Troubleshooting

- `Database connection failed`: verify `DATABASE_URL` in `.env` and ensure PostgreSQL is running.
- `422 Unprocessable Entity`: request body must contain exactly one of `url` or `identifier`, and the identifier must be `owner/repository`.
- `409 Conflict`: repository already exists in the database.
- `503 Service Unavailable`: GitHub API requests timed out or could not connect.

## Notes

- `.env.example` shows the required configuration values.
- The app uses `pytest-asyncio` for async tests.
