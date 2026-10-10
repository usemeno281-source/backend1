# Urban Infrastructure Priority Engine

Backend API for the OFFGRID smart-city hackathon project. This is a small FastAPI app meant to run on your computer while the frontend is built separately.

## Project structure

```text
urban-infrastructure-priority-engine/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS, and endpoints
│   └── models.py        # Pydantic request/response models
├── .env.example         # Placeholder config only
├── .gitignore
├── README.md
└── requirements.txt
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/issues` | Create a new infrastructure issue |
| GET | `/issues` | List all submitted issues |
| GET | `/issues/{issue_id}` | Get one issue by ID |
| GET | `/docs` | Interactive API docs (built into FastAPI) |

Issues are stored **in memory only**. Restarting the server deletes all submitted issues. Persistent storage (for example Supabase) is not connected yet.

## Setup on Windows (PowerShell)

Open PowerShell in this project folder, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

If PowerShell blocks the virtual environment, run this once, then try activation again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Run the API

With the virtual environment activated:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

- Welcome: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/health
- Issues: http://127.0.0.1:8000/issues
- Docs: http://127.0.0.1:8000/docs

## CORS for the separate frontend

Copy `.env.example` to `.env` and set `ALLOWED_ORIGINS` to the exact frontend URL(s), separated by commas.

- Local development: if `ALLOWED_ORIGINS` is empty and `APP_ENV` is not `production`, the API allows common localhost origins (`3000`, `5173`, `5500`, `8080`).
- Vercel: add the deployed frontend URL, for example `https://your-frontend.vercel.app`.
- Production: set `APP_ENV=production` and list exact origins. The API will not allow `*` in production.

Restart the server after changing `.env`.

Stop the server with `Ctrl+C`.

## Setup on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Notes

- `.env` is ignored by git. Keep real secrets there, never in `.env.example`.
- This backend is not connected to Supabase yet.
- No sample city infrastructure data is included.
- Submitted issues exist only while the server is running.
