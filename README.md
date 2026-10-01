# MailPilot AI

MailPilot AI is a React/Vite frontend and FastAPI backend.

## Deploy with Vercel, Render, and PostgreSQL

The repository includes a Render Blueprint at [`render.yaml`](./render.yaml) and a
Vercel SPA rewrite at [`frontend/vercel.json`](./frontend/vercel.json).

### 1. Deploy the backend and database

1. Push this repository to GitHub.
2. In Render, create a new Blueprint and select this repository. Render will read
   `render.yaml` and create the `mailpilot-api` service and `mailpilot-db`
   PostgreSQL database.
3. Review Render's plan and current pricing before applying the Blueprint. The
   included service and database plans are paid plans.
4. After deployment, open the backend URL and confirm
   `https://<backend-host>/health/` returns a healthy status.
5. Set `CORS_ORIGINS` on the Render service to the exact Vercel origin, such as
   `https://<your-project>.vercel.app` (no trailing slash). Add any custom
   frontend domains as comma-separated origins, then redeploy the backend.
6. Set the optional `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and
   `GEMINI_API_KEY` values in Render if those integrations are needed.

Render generates `SECRET_KEY` and connects the service to the managed database.
Do not commit production secrets or a production `.env` file.

### 2. Deploy the frontend

1. In Vercel, import the same GitHub repository.
2. Set the project **Root Directory** to `frontend`.
3. Use the detected Vite build settings: build command `npm run build` and output
   directory `dist`.
4. Add the environment variable `VITE_API_BASE_URL` with the deployed backend
   URL, for example `https://<backend-host>`. Redeploy after setting it.
5. Copy the Vercel deployment origin into Render's `CORS_ORIGINS` as described
   above. If you use a custom domain, include that origin too.

The Vercel rewrite serves the React app for client-side routes such as
`/dashboard` and `/inbox`.

### Local development

- Frontend: `cd frontend`, `npm ci`, `npm run dev`
- Backend: `cd Backend`, create and activate a Python virtual environment, install
  `requirements.txt`, copy `.env.example` to `.env`, configure a local
  PostgreSQL `DATABASE_URL`, then run `uvicorn app.main:app --reload`.

## Current application scope

This deployment publishes the existing project as it is; it does not turn the
backend scaffolds into a complete production API. The FastAPI app currently
registers the root and health endpoints only, and several frontend services use
mock data. Verify the intended live authentication, email, task, and AI flows
before treating the deployment as a production-ready MailPilot service.
