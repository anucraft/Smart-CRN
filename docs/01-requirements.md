# 1. Requirements and Analysis

## Problem statement
A WooCommerce store owner manages customers and orders inside the WordPress admin, which is built for *fulfilling orders*, not for *understanding customers*. There is no single screen that shows "who are my best customers, what did they buy, what did we say to them, and what is happening today". Owners end up exporting CSV files, keeping notes in spreadsheets, and checking several admin pages by hand.

## Project goals
| # | Goal | How we measure it |
|---|------|-------------------|
| G1 | Mirror WooCommerce customers, orders and products automatically | A new order appears in the CRM within seconds via webhook |
| G2 | Give the owner one dashboard with the numbers that matter | Dashboard shows customers, orders, revenue, pending orders, monthly sales |
| G3 | Make each customer's history and context easy to find | Customer page shows orders, timeline and private notes |
| G4 | Stay simple to run | One backend process, one SQLite file, one static frontend |

## Business objectives
- Save the owner time otherwise spent on exports and manual lookups.
- Improve repeat sales by making VIP and returning customers visible (segments).
- Keep staff knowledge in the system (notes) instead of in people's heads.
- Offer a low-cost alternative to heavyweight CRMs for small stores.

## Scope
**In scope (this MVP):** authentication, dashboard, customers, customer detail with timeline and notes, orders, products (read-only), analytics, WooCommerce sync (manual + webhooks), settings.
**Out of scope:** AI features (removed on purpose; see roadmap), sending email, writing data back to WooCommerce, multi-user roles, multi-store.

## Functional requirements
| ID | Requirement |
|----|-------------|
| FR-1 | An admin can log in and log out. Every page except login is protected. |
| FR-2 | The dashboard shows total customers, total orders, revenue, pending orders, a 12-month sales chart and recent activity. |
| FR-3 | Customers can be listed, searched (name, email, phone, city), filtered by segment (VIP, returning, new, no orders) and sorted. |
| FR-4 | A customer profile shows contact details, lifetime stats, recent orders, a timeline and notes. |
| FR-5 | Admins can add and delete private notes on a customer. |
| FR-6 | Orders can be listed, searched (number, customer name or email) and filtered by status. |
| FR-7 | An order page shows items, totals, payment status, shipping status, addresses and the customer. |
| FR-8 | The CRM can sync customers, orders and products from WooCommerce on demand. |
| FR-9 | The CRM receives WooCommerce webhooks and updates data in near real time; requests are verified by signature. |
| FR-10 | Analytics show revenue, orders per month, customer growth and top customers. |
| FR-11 | An admin can save and test WooCommerce credentials from the UI. Secrets are never sent back to the browser. |

## Non-functional requirements
| Area | Requirement |
|------|-------------|
| Security | Passwords hashed (Werkzeug); JWT auth; webhook HMAC-SHA256 verification with constant-time compare; secrets only in env/DB, never in the frontend; CORS limited to configured origins. |
| Reliability | Sync and webhook handlers are idempotent; sync commits per page so a failure keeps earlier progress. |
| Performance | List endpoints paginate (max 100/page). Customer stats are computed in one SQL aggregate, not N+1 queries. |
| Maintainability | Layered backend (routes, services, models); app factory; automated tests (31); documented API. |
| Usability | Responsive layout, keyboard focus styles, labelled form fields, reduced-motion respected, clear empty and error states. |
| Portability | Standard SQLAlchemy; moving from SQLite to PostgreSQL means changing `DATABASE_URL`. |
| Limits (accepted for MVP) | Single admin role; synchronous sync inside a request; SQLite single-writer. |

## Competitor analysis
(High-level and qualitative. Check current features and pricing before quoting them in a pitch.)

| Option | Strength | Gap SmartCRM addresses |
|--------|----------|------------------------|
| WooCommerce admin and built-in Analytics | Already installed; accurate order data | Not customer-centric: no notes, no timeline, no segments |
| Metorik | Deep WooCommerce analytics and engagement tools | Paid SaaS, broader than a small shop needs |
| FluentCRM and similar WordPress plugins | Email automation inside WordPress | Runs inside WordPress, adds load to the shop server, tied to WordPress |
| HubSpot / Zoho CRM + connector | Full-featured CRMs | Heavy setup, general-purpose, order data feels bolted on |
| **SmartCRM** | Small, self-hostable, WooCommerce-first, one dashboard | Intentionally limited feature set (MVP) |

## Technology justification
| Choice | Why it fits this project | Alternative considered |
|--------|--------------------------|------------------------|
| React + Vite | Fast dev server and build; component model suits dashboards | Next.js: SSR not needed for a private admin app |
| Tailwind CSS 4 | Consistent design tokens, no custom CSS sprawl | Component libraries: faster to start, harder to give a distinct look |
| React Router | Standard client routing, supports protected routes | n/a |
| Axios | Interceptors give one place to attach the JWT and handle 401 | `fetch`: needs hand-written wrappers |
| Framer Motion | Small, purposeful transitions (page fade, note add/remove) | CSS transitions |
| Chart.js (+ react-chartjs-2) | Light, canvas-based, enough chart types | Recharts: heavier |
| Flask | Minimal, easy to explain; blueprints give structure | FastAPI: excellent, but Flask was the required stack |
| SQLAlchemy | ORM with portable SQL; relationships and aggregates | Raw SQL: more code, less portable |
| Flask-JWT-Extended | Mature JWT handling | Session cookies: need CSRF handling across Vercel/Render domains |
| Flask-CORS | Frontend and backend are on different domains | n/a |
| SQLite | Zero setup, one file, perfect for a demo | PostgreSQL: recommended for production (see roadmap) |
| requests | Simple, reliable HTTP client for the WooCommerce API | `woocommerce` PyPI package: thin wrapper that hides pagination details we want to control |
| pytest | Readable tests, fixtures | unittest |

Extra libraries beyond your list, and why: `python-dotenv` (load `.env`), `requests` (call WooCommerce), `gunicorn` (production server on Render), `pytest` (tests), `react-chartjs-2` (React wrapper for Chart.js).
