# 7. Setup from scratch (every command explained)

These are the commands used to create this project. If you cloned the finished repo, skip to **"Run it"** at the end.

Prerequisites: Python 3.11+, Node.js 20+, Git. Check with `python3 --version`, `node --version`, `git --version`.

## A. Project root
```bash
mkdir smartcrm && cd smartcrm      # create the repo folder and enter it
mkdir docs                         # documentation lives in the repo
```

## B. Backend
```bash
mkdir backend && cd backend
python3 -m venv .venv
```
`venv` creates an isolated Python environment in `.venv/`, so this project's packages don't clash with other projects.

```bash
source .venv/bin/activate          # macOS/Linux
# Windows PowerShell:  .venv\Scripts\Activate.ps1
```
Activating puts the venv's `python` and `pip` first on your PATH. Your prompt shows `(.venv)`.

```bash
pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Cors python-dotenv requests gunicorn
```
| Package | Why |
|---------|-----|
| Flask | Web framework |
| Flask-SQLAlchemy | SQLAlchemy ORM integrated with Flask |
| Flask-JWT-Extended | Create and verify JWTs |
| Flask-Cors | Allow the Vercel frontend origin to call the Render API |
| python-dotenv | Load `.env` into environment variables |
| requests | Call the WooCommerce REST API |
| gunicorn | Production WSGI server (Render runs this) |

```bash
pip install pytest                 # test runner (development only)
pip freeze > requirements.txt      # record exact versions so everyone installs the same thing
```
In this repo `pytest` and its helpers are removed from `requirements.txt` and kept in `requirements-dev.txt` (which starts with `-r requirements.txt`), so production installs stay small.

```bash
mkdir -p app/models app/routes app/services app/utils tests
```
`-p` creates parent folders and doesn't fail if they exist. Files are then added as described in [06-project-structure.md](06-project-structure.md).

```bash
cp .env.example .env               # create your private config (never commit .env)
```
Edit `.env` and set long random values for `SECRET_KEY` and `JWT_SECRET_KEY`. Generate one with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**How Flask is configured:** `wsgi.py` calls `create_app()`; `.flaskenv` contains `FLASK_APP=wsgi.py` so the `flask` command knows where the app is; `config.py` reads everything else from `.env`.

## C. Frontend
```bash
cd ..                              # back to the project root
npm create vite@latest frontend -- --template react
```
Generates a React project using Vite (`--template react`). If it asks questions, choose React with JavaScript.
```bash
cd frontend
npm install                        # install the template's dependencies
npm install axios react-router-dom framer-motion chart.js react-chartjs-2
npm install tailwindcss @tailwindcss/vite
```
| Package | Why |
|---------|-----|
| axios | HTTP client with interceptors for the JWT |
| react-router-dom | Pages and protected routes |
| framer-motion | Small transitions |
| chart.js + react-chartjs-2 | Charts and their React wrapper |
| tailwindcss + @tailwindcss/vite | Utility CSS (v4 uses a Vite plugin, no `tailwind.config.js` or PostCSS file) |

Then: add the plugin in `vite.config.js` (`plugins: [react(), tailwindcss()]`) and put `@import "tailwindcss";` at the top of `src/index.css`.
```bash
cp .env.example .env               # VITE_API_URL=http://localhost:5000/api
```
Vite only exposes variables that start with `VITE_` to browser code. **Never put secrets in them**; they are public.

## D. Git and GitHub
```bash
cd ..                              # project root
git init                           # start tracking changes in this folder
git branch -M main                 # name the default branch "main"
```
A `.gitignore` (already in the repo) stops `.env`, `.venv/`, `node_modules/`, `dist/` and `*.db` from being committed.
```bash
git add .                          # stage every non-ignored file
git commit -m "chore: initial project"   # save a snapshot with a message
```
Create an empty repository on github.com (no README, no .gitignore), then:
```bash
git remote add origin https://github.com/<you>/smartcrm.git   # name the remote "origin"
git push -u origin main                                         # upload and remember the link
```
**Commit message style:** [Conventional Commits](https://www.conventionalcommits.org): `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`. Small commits, one idea each.

## E. Run it
Terminal 1: backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env                                  # then edit secrets
flask create-admin --email you@shop.com --name "You"  # prompts for a password
flask seed-demo                                       # OPTIONAL fake data so you can demo without a store
flask run --debug                                     # http://localhost:5000
```
Terminal 2: frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev                                           # http://localhost:5173
```
Run backend tests: `cd backend && pytest`. Frontend production build check: `cd frontend && npm run build`.

**Using a real store:** log in, open **Settings**, paste the store URL and REST API keys, click **Test connection**, then **Sync everything**. For live updates, create webhooks as described on the Settings page. WooCommerce cannot reach `localhost`, so deploy the backend (see [09-deployment.md](09-deployment.md)) or use a tunnel such as ngrok.

**Demo data note:** `seed-demo` creates fake customers with IDs that look like WooCommerce IDs. Use `flask seed-demo --reset` to wipe and re-create, and do not mix demo data with a real sync (use a fresh database, or `--reset` then sync).
