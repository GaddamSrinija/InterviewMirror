# Interview Mirror

Interview Mirror imports a GitHub repository, generates an AI-driven mock technical interview based on its actual code, runs the interview, and produces a scored analysis report of the candidate's answers.

**Stack:** FastAPI + PostgreSQL (pgvector) on the backend, React + Vite + Tailwind on the frontend, OpenRouter for LLM calls.

---

## 1. Prerequisites

Install these before you start:

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12 | Earlier 3.x versions may work but are untested here |
| Node.js | 18+ | Needed for Vite 6 |
| PostgreSQL | 14+ | Must support the `pgvector` extension |
| Git | any recent version | |

You will also need:
- An **OpenRouter API key** — https://openrouter.ai/keys (used for interview question generation and answer analysis)
- A **GitHub personal access token** *(optional but recommended)* — https://github.com/settings/tokens (only needed to avoid GitHub's low unauthenticated rate limit when importing repos)

---

## 2. Clone the repo

```bash
git clone <your-repo-url>
cd InterviewMirror_FINAL
```

---

## 3. Database setup

Interview Mirror uses PostgreSQL with the `pgvector` extension (for embedding-based code search). You do **not** need to manually create the extension — the first migration does that for you (`CREATE EXTENSION IF NOT EXISTS vector`).

This project is built and tested against **[Neon](https://neon.tech)** (managed serverless Postgres), which supports `pgvector` out of the box. To set up your database:

1. Create a free account at https://neon.tech.
2. Create a new project (this gives you a database automatically — no need to run `CREATE DATABASE` manually).
3. From the Neon dashboard, copy your connection string. It looks like:
   ```
   postgresql://<user>:<password>@<endpoint>.neon.tech/<dbname>?sslmode=require
   ```
4. You'll paste this into `backend/.env` as `DATABASE_URL` in the next step — but **change the prefix** from `postgresql://` to `postgresql+asyncpg://`, since the backend uses the async SQLAlchemy driver. For example:
   ```
   DATABASE_URL=postgresql+asyncpg://<user>:<password>@<endpoint>.neon.tech/<dbname>?ssl=require
   ```
   Note `asyncpg` expects `?ssl=require`, not `?sslmode=require` — Neon's copied string uses `sslmode`, which you need to change to `ssl` or `asyncpg` will error on connect.

> **Prefer local/self-hosted Postgres instead?** That works too — install Postgres 14+ and the `pgvector` extension yourself (https://github.com/pgvector/pgvector#installation), then create a database with `psql -U postgres -c "CREATE DATABASE interview_mirror;"` and use a local `DATABASE_URL` instead of Neon's.

---

## 4. Backend setup

All commands below are run from the `backend/` folder.

```bash
cd backend
```

### 4.1 Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your prompt after this.

### 4.2 Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on bcrypt:** `requirements.txt` pins `bcrypt==4.0.1` alongside `passlib==1.7.4`. Do not upgrade `bcrypt` independently — versions 4.1+ break passlib 1.7.4's internal backend detection and will crash password hashing with a `ValueError`/`AttributeError` at runtime, not at install time.

### 4.3 Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/interview_mirror
JWT_SECRET=replace-with-a-long-random-string
GITHUB_TOKEN=ghp_your_personal_access_token
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
OPENROUTER_CHAT_MODEL=google/gemini-2.5-flash
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small
STORAGE_DIR=storage
FRONTEND_URL=http://localhost:5173
```

- `DATABASE_URL` — update the username/password/port/db-name to match your local Postgres.
- `JWT_SECRET` — any long random string; used to sign auth tokens.
- `GITHUB_TOKEN` — optional. Leave blank to still work, but you'll hit GitHub's 60-requests/hour unauthenticated limit fast.
- `OPENROUTER_API_KEY` — required. Get one at https://openrouter.ai/keys. **Note:** having a key does not mean requests are free — most models (including the default `google/gemini-2.5-flash`) draw from a paid credit balance. Add a small amount of credit at https://openrouter.ai/settings/credits, or swap `OPENROUTER_CHAT_MODEL` to a `:free`-suffixed model for local testing (check current free models at https://openrouter.ai/models).
- `FRONTEND_URL` — must match wherever the frontend actually runs (default Vite dev port is `5173`), since it's used for CORS.

### 4.4 Run database migrations

```bash
alembic upgrade head
```

This creates all tables and enables the `pgvector` extension. If this fails with an error mentioning `extension "vector" is not available`, your Postgres server doesn't have pgvector installed — go back to step 3.

### 4.5 Start the backend

```bash
uvicorn app.main:app --reload --reload-dir app
```

**Important:** always include `--reload-dir app`. Running bare `uvicorn app.main:app --reload` from inside `backend/` makes the file watcher scan the entire folder, including `venv/` (tens of thousands of files) — this causes a reload crash loop where the server restarts itself repeatedly and never finishes starting. Scoping the watcher to `app/` avoids this entirely.

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
[info     ] interview_mirror_starting
INFO:     Application startup complete.
```

Verify it's up:
```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

Leave this terminal running. Interactive API docs are available at `http://localhost:8000/docs`.

---

## 5. Frontend setup

Open a **new terminal** (keep the backend running in the first one).

```bash
cd frontend
```

### 5.1 Install dependencies

```bash
npm install
```

### 5.2 Configure environment variables

```bash
cp .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

This must point at your running backend from step 4.5.

### 5.3 Start the frontend

```bash
npm run dev
```

Vite will print a local URL, typically:
```
Local:   http://localhost:5173/
```

Open that URL in your browser.

---

## 6. Verify everything works end-to-end

1. Open `http://localhost:5173`.
2. Register a new account.
3. Import a public GitHub repo (a small one first, to keep API/LLM calls cheap).
4. Start a mock interview and answer a question.
5. Check the generated report.

If step 2 (register) fails with a 500 error mentioning `bcrypt`, see the note in section 4.2 — you likely have an unpinned/upgraded `bcrypt`. Run:
```bash
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

If any LLM-dependent step (question generation, analysis) fails with an HTTP 402 error mentioning OpenRouter credits, your OpenRouter account balance is too low — see the `OPENROUTER_API_KEY` note in section 4.3.

---

## 7. Running tests (backend)

```bash
cd backend
pytest
```

---

## 8. Project structure

```
InterviewMirror_FINAL/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── llm/          # LLM provider abstraction (OpenRouter)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic (auth, GitHub import, interviews, reports, storage)
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── alembic/          # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios client
│   │   ├── components/
│   │   ├── context/       # Auth context
│   │   ├── pages/
│   │   └── App.jsx
│   ├── package.json
│   └── .env.example
└── README.md
```


