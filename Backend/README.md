# MailPilot Backend (scaffold)

This folder contains a scaffold of the backend application used by the MailPilot project.

To run locally:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Before starting the API, edit `.env` and set `DATABASE_URL` to a reachable
PostgreSQL database URL and `SECRET_KEY` to a long random value. The API uses
`CORS_ORIGINS` to allow the frontend origin; for local Vite development, the
example already allows `http://localhost:5173`.
