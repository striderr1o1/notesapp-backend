# Likho - Backend

Likho is a note-taking application that organizes user content into **notebooks** and **notes**. This repository contains the backend API built with FastAPI.

## Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** MongoDB Atlas (via PyMongo)
- **Session Store:** Redis
- **Authentication:** Session-based with bcrypt password hashing
- **Validation:** Pydantic v2

## Project Structure

```
backend/
├── main.py                        # FastAPI app entry point, CORS config, router registration
├── auth/
│   └── auth.py                    # Authentication logic (signup, login, logout, session validation)
├── database/
│   ├── authorizationDB.py         # MongoDB connector for user accounts (auth database)
│   ├── mongo_db.py                # MongoDB connector for notebooks & notes (app-data database)
│   └── redis_db.py                # Redis connector for session management
├── routes/
│   ├── auth_routes.py             # Auth endpoints: /signup, /login, /logout
│   └── notes_routes.py            # Notes endpoints: CRUD for notebooks and notes
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (not committed)
└── .gitignore
```

## Architecture

### Overview

The application follows a layered architecture with clear separation of concerns:

```
Routes (API layer)  →  Auth (business logic)  →  Database connectors (data layer)
```

- **Routes** define API endpoints and use Pydantic models for request validation.
- **Auth** handles password hashing (bcrypt), session creation/validation, and user management.
- **Database connectors** encapsulate all direct database operations. There are three:
  - `authorizationDB.py` — MongoDB `auth` database, stores user credentials and notebook references.
  - `mongo_db.py` — MongoDB `app-data` database, stores notebooks and notes.
  - `redis_db.py` — Redis, stores session keys with a 7-day TTL.

### Authentication Flow

1. **Signup** — Password is hashed with bcrypt and stored in MongoDB.
2. **Login** — Password is verified against the stored hash. On success, a UUID session ID is created in Redis and returned as an `HttpOnly` cookie.
3. **Protected routes** — Use FastAPI's `Depends()` to call `validate_session`, which extracts the session ID from cookies, looks up the user in Redis, and fetches the full user document from MongoDB.
4. **Logout** — Deletes the session from Redis, invalidating the cookie.

### Data Model

**User** (MongoDB `auth.username_passwords`):
```
{ username, password (hashed), email, notebook_ids: [ObjectId] }
```

**Notebook** (MongoDB `app-data.notebooks`):
```
{ _id, username, notebook_name, created_at, notes: [note_id] }
```

**Note** (MongoDB `app-data.notes`):
```
{ _id, notename, username, notebook_id, data }
```

**Session** (Redis):
```
key: UUID session_id  →  value: username  (TTL: 7 days)
```

## API Endpoints

### Authentication

| Method | Endpoint         | Description              | Auth Required |
|--------|------------------|--------------------------|---------------|
| POST   | `/signup`        | Register a new user      | No            |
| POST   | `/login`         | Login, returns session cookie | No       |
| GET    | `/logout`        | Invalidate session       | Yes           |
| GET    | `/check_session` | Verify session is valid  | Yes           |

### Notebooks & Notes

| Method | Endpoint           | Description                        | Auth Required |
|--------|--------------------|------------------------------------|---------------|
| GET    | `/getnotebooks`    | Get all notebooks for the user     | Yes           |
| POST   | `/createnotebook`  | Create a new notebook              | Yes           |
| POST   | `/deletenotebook`  | Delete a notebook and all its notes| Yes           |
| POST   | `/createnote`      | Create a note inside a notebook    | Yes           |
| POST   | `/getnotes`        | Get all notes in a notebook        | Yes           |
| POST   | `/getnotefromid`   | Get a single note by ID            | Yes           |
| PUT    | `/replacenote`     | Update a note's contents           | Yes           |
| POST   | `/deletenote`      | Delete a note                      | Yes           |

## Setup

### Prerequisites

- Python 3.11+
- A MongoDB Atlas cluster
- A running Redis instance
- (Optional) Conda or virtualenv

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/striderr1o1/notesapp-backend.git
   cd notesapp-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root with the following variables:
   ```
   MONGO_USERNAME=<your_atlas_username>
   MONGO_PASSWORD=<your_atlas_password>
   REDIS_HOST=<your_redis_host>
   REDIS_PORT=<your_redis_port>
   ```

5. **Ensure your IP is whitelisted** in MongoDB Atlas under Network Access.

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs are served at `/docs` (Swagger UI).

## Known Issues (Analyzed by Claude Opus)

1. **Multiple session IDs per user** — Logging in multiple times creates multiple Redis sessions for the same user. There is no mechanism to invalidate previous sessions on new login, which could lead to unbounded session accumulation.

2. **Duplicate connector instances** — Both `auth_routes.py` and `notes_routes.py` independently instantiate `mongo_db_auth_connector` and `redis_connector`, creating separate MongoDB and Redis connections instead of sharing a single instance across the application.

3. **No cookie clearing on logout** — The `/logout` endpoint deletes the session from Redis but does not clear the `session_id` cookie from the client response. The client retains a stale cookie.

4. **Inconsistent HTTP methods for destructive operations** — `/deletenote` and `/deletenotebook` use `POST` instead of `DELETE`, which doesn't follow REST conventions.

5. **Unreachable code after `raise`** — In `auth.py` (`validate_session`) and `notes_routes.py` (`Check_Auth`), there are `return` statements after `raise HTTPException(...)` that can never execute.

6. **Missing error handling for `None` notebooks in listing** — In `/getnotebooks`, if `get_notebook_data` returns `None` (e.g., a notebook was deleted but its ID remains in the user document), `None` is appended to the list without being filtered out.

7. **No input sanitization or length limits** — Pydantic models validate types but don't enforce length constraints on usernames, passwords, notebook names, or note content.

8. **`datetime.utcnow()` is deprecated** — In `mongo_db.py`, `datetime.utcnow()` is used for `created_at` timestamps. This has been deprecated since Python 3.12 in favor of `datetime.now(datetime.UTC)`.
