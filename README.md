# CareerGraph

CareerGraph is an AI job-search analyst for retrieving, ranking, and analyzing relevant job opportunities against a candidate profile.

The current repository is an initial development scaffold. The product requirements and architectural notes are in [`careergraph_ai_agent_project_brief.md`](./careergraph_ai_agent_project_brief.md).

## Stack

- FastAPI backend
- Next.js frontend
- PostgreSQL for relational data
- Qdrant for vector search
- Docker Compose for local development

## Local Setup

1. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Start the services:

   ```powershell
   docker compose up --build
   ```

3. Open the frontend:

   ```txt
   http://localhost:3000
   ```

The backend is available at:

```txt
http://localhost:8000
```

Qdrant is available at:

```txt
http://localhost:6333/dashboard
```

## Database Migrations

For local backend work outside Docker, run migrations before starting the API:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.db.migrations
```

The initial baseline migration lives in:

```txt
backend/alembic/versions/0001_initial_schema.py
```

## Initial Layout

```txt
backend/
  app/
    __init__.py
    config.py
    main.py
  tests/
  Dockerfile
  requirements.txt
frontend/
  app/
    globals.css
    layout.tsx
    page.tsx
  Dockerfile
  package.json
docker-compose.yml
.env.example
```
