# SmartCRM: a lightweight CRM for WooCommerce

SmartCRM mirrors the customers, orders and products of a WooCommerce store into its own database and gives the owner one dashboard for them: search and segment customers, read their history, leave private notes, watch sales, and see new orders arrive in real time through webhooks.

> This build covers the WooCommerce integration only. AI features were intentionally left out (see [roadmap](docs/08-roadmap-risks.md)).

## Features
| Module | What you get |
|--------|--------------|
| Authentication | JWT login, logout, protected routes |
| Dashboard | Customers, orders, revenue, pending orders, average order, 12-month sales chart, recent activity |
| Customers | Search, segments (VIP / returning / new / no orders), sort, profile, timeline, private notes |
| Orders | Search, status filter, order detail with items, payment status, shipping status, addresses |
| Products | Searchable catalogue with stock |
| Analytics | Revenue, orders per month, customer growth, top customers |
| WooCommerce | Manual sync (all / customers / orders / products), HMAC-verified webhook receiver, connection test, credentials managed in the UI |

## Tech stack
React 19 · Vite · Tailwind CSS 4 · React Router · Axios · Framer Motion · Chart.js · Flask · SQLAlchemy · Flask-JWT-Extended · Flask-CORS · SQLite · WooCommerce REST API v3 + webhooks. Deploy: Vercel (frontend), Render (backend). See [why each was chosen](docs/01-requirements.md#technology-justification).

## Quick start
You need Python 3.11+, Node 20+ and Git.

```bash
# 1. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.example .env                                     # set SECRET_KEY and JWT_SECRET_KEY
flask create-admin --email you@shop.com --name "You"     # asks for a password
flask seed-demo                                          # optional: fake store data for a demo
flask run --debug                                        # http://localhost:5000

# 2. Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev                                              # http://localhost:5173
```
Log in with the admin you just created. With `seed-demo` the dashboard is populated immediately. To use a real store, go to **Settings** and follow the on-screen steps.

Run the tests: `cd backend && pytest` (31 tests).

## Documentation
| Doc | Contents |
|-----|----------|
| [01 Requirements](docs/01-requirements.md) | Problem, goals, business objectives, functional and non-functional requirements, competitors, technology justification |
| [02 Architecture](docs/02-architecture.md) | Layers, request, authentication, sync and webhook flows (Mermaid) |
| [03 Database](docs/03-database.md) | ER diagram, why each table exists, business definitions |
| [04 API](docs/04-api.md) | Every endpoint with request and response |
| [05 UI](docs/05-ui-pages.md) | Pages, user flow, navigation |
| [06 Structure](docs/06-project-structure.md) | Every folder and file explained |
| [07 Setup](docs/07-setup-from-scratch.md) | Every command from scratch, explained |
| [08 Roadmap and risks](docs/08-roadmap-risks.md) | Phases, timeline, risks, limitations, future scope |
| [09 Deployment](docs/09-deployment.md) | Render, Vercel, WooCommerce webhook setup, troubleshooting |

## Key design decisions
- **Layered backend** (routes → services → models) so business rules are testable without HTTP.
- **Idempotent upserts** shared by bulk sync and webhooks, so retries and duplicate deliveries are harmless.
- **WooCommerce is the source of truth**, so customers and orders are read-only in the CRM; only notes are written locally.
- **Derived values** (payment/shipping status, spend, segment) are computed, not stored, so they can't go stale.
- **Webhook security** by HMAC-SHA256 signature over the raw body with a constant-time comparison.

## Known limitations
SQLite on Render's free tier is ephemeral (see [risks](docs/08-roadmap-risks.md)); single admin role; sync runs inside the request. Sync and webhook logic are verified against realistic mock payloads and a local fake WooCommerce server, so test against your own store before presenting.

## License
MIT (add a LICENSE file if you publish this).
