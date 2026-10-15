# 9. Deployment (Render + Vercel)

## Order of operations
1. Deploy the **backend** first (you need its URL).
2. Deploy the **frontend** with that URL.
3. Come back and allow the frontend origin in the backend's CORS.

## Backend on Render (Web Service)
1. Push the repo to GitHub.
2. Render → **New → Web Service** → pick the repo.
3. Settings:
   | Field | Value |
   |-------|-------|
   | Root Directory | `backend` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn wsgi:app --workers 2 --timeout 120` |
   | Health Check Path | `/api/health` |
4. Environment variables:
   | Key | Value |
   |-----|-------|
   | `SECRET_KEY`, `JWT_SECRET_KEY` | Long random strings (different from each other) |
   | `CORS_ORIGINS` | Your Vercel URL, e.g. `https://smartcrm.vercel.app` (comma-separate several) |
   | `DATABASE_URL` | Leave empty for SQLite, or a PostgreSQL URL (recommended for anything beyond a demo; add `psycopg2-binary` to `requirements.txt`) |
   | `PYTHON_VERSION` | e.g. `3.12.3` if you need to pin it |
5. Create the first admin from the Render **Shell** tab: `flask create-admin --email you@shop.com --name You`. Optionally `flask seed-demo`.

`--timeout 120` gives a long first sync room to finish. Remember the **SQLite persistence warning** in [08-roadmap-risks.md](08-roadmap-risks.md).

## Frontend on Vercel
1. Vercel → **Add New → Project** → pick the repo.
2. Root Directory: `frontend`. Framework preset: Vite (auto-detected). Build `npm run build`, output `dist`.
3. Environment variable: `VITE_API_URL` = `https://<your-render-service>.onrender.com/api`.
4. `frontend/vercel.json` already rewrites every path to `index.html`, so refreshing `/customers/5` works.
5. Redeploy after changing environment variables (Vite bakes them in at build time).

## Connect WooCommerce
1. WooCommerce → Settings → Advanced → **REST API** → Add key (Read) → copy key and secret.
2. In SmartCRM → **Settings**: paste store URL, key, secret, and choose a webhook secret. Save, **Test connection**, **Sync everything**.
3. WooCommerce → Settings → Advanced → **Webhooks** → Add webhook, six times:
   | Topic | Delivery URL | Secret |
   |-------|--------------|--------|
   | Order created / Order updated | `https://<render-url>/api/woocommerce/webhook` | the webhook secret from step 2 |
   | Customer created / Customer updated | same | same |
   | Product created / Product updated | same | same |
4. Place a test order. It should appear in SmartCRM within seconds. If it doesn't, check the webhook's delivery log in WooCommerce (it shows the HTTP status your backend returned).

## Troubleshooting
| Symptom | Likely cause |
|---------|--------------|
| Browser console: CORS error | `CORS_ORIGINS` doesn't exactly match the Vercel URL (scheme, no trailing slash) |
| Login works locally, fails in production | `VITE_API_URL` missing or lacks `/api`; redeploy the frontend |
| Webhook returns 401 | Secret in WooCommerce differs from the one saved in SmartCRM |
| Webhook returns 503 | No webhook secret saved yet |
| "WooCommerce rejected the API keys" | Wrong key/secret, or key lacks Read permission |
| Everything vanished after a deploy | Ephemeral SQLite on free Render; see risk table |
