## ccbda-crud

Simple FastAPI CRUD API that stores items with a name and email in a local JSON file.

## Project Structure

This repo has two parts:

- `backend/` (FastAPI)
- `frontend/` (React + Next.js)

## Backend

Install:

```bash
cd backend
cp env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run:

```bash
cd backend
uvicorn main:app --reload
```

The backend uses `backend/pyproject.toml` for metadata and dependencies.
The server listens on `http://127.0.0.1:8000` when running locally.
The API enables CORS for the Next.js dev server at `http://localhost:3000` and `http://127.0.0.1:3000` so the browser can call the API from a different origin during development. Edit `backend/.env` to change `CORS_ALLOW_ORIGINS`.
The backend reads environment variables from `backend/.env`.

Environment:

- Backend env file: `backend/.env` (based on `backend/env.example`)

## Backend examples

Create an item:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com"}'
```

List items:

```bash
curl http://127.0.0.1:8000/
```

Get an item:

```bash
curl http://127.0.0.1:8000/1
```

Update an item:

```bash
curl -X PUT http://127.0.0.1:8000/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Byron","email":"ada.b@example.com"}'
```

Delete an item:

```bash
curl -X DELETE http://127.0.0.1:8000/1
```

Data is persisted in `backend/items.json`.

## Frontend (Next.js)

Install:

```bash
cd frontend
cp env.example .env
npm install
```

Run:

```bash
cd frontend
npm run dev
```

The frontend talks to the API at `http://127.0.0.1:8000` by default when running locally and runs on `http://localhost:3000`.

To point the UI at a different API base URL, edit `frontend/.env` and update `BACKEND_URLS`.
The frontend reads environment variables from `frontend/.env`.

Environment:

- Frontend env file: `frontend/.env` (based on `frontend/env.example`)

## Local Defaults

When running locally, the default URLs are:

- Backend API: `http://127.0.0.1:8000`
- Frontend UI: `http://127.0.0.1:3000`

If you see `sh: next: command not found`, run `npm install` inside `frontend/` to install dependencies.
