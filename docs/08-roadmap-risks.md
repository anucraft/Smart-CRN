# 8. Roadmap, timeline, risks and future scope

## Development roadmap (phases)
| Phase | Deliverable | Commit style |
|-------|-------------|--------------|
| 0. Planning | Requirements, architecture, ER diagram, API design, folder structure | `docs: add requirements and architecture` |
| 1. Backend foundation | App factory, config, models, JWT auth, CLI | `feat(backend): app factory, models, auth` |
| 2. Core API | Customers, orders, products, notes, timeline, analytics | `feat(api): customers, orders, analytics` |
| 3. WooCommerce | Client, sync, webhook, settings | `feat(woo): sync and webhook receiver` |
| 4. Quality | Tests with realistic payloads, demo seed | `test: backend suite` |
| 5. Frontend | Auth shell, pages, charts | `feat(ui): ...` |
| 6. Ship | Deployment, README, demo rehearsal | `docs: deployment guide` |

## Suggested hackathon timeline (adjust to your clock)
| Share of time | Focus |
|---------------|-------|
| 0-10% | Plan, diagrams, repo setup |
| 10-40% | Backend: models, auth, API, WooCommerce sync + webhook |
| 40-70% | Frontend pages |
| 70-85% | Tests, bug fixing, seed data, connect a real or test WooCommerce store |
| 85-100% | Deploy, README polish, demo script, screenshots |

## Risk analysis
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **SQLite on Render's free tier loses data** (the filesystem is ephemeral and resets on deploy/restart) | High | High | Everything synced from WooCommerce can be re-synced, but **notes and admin accounts are lost**. Use a persistent disk (paid) or point `DATABASE_URL` at free managed PostgreSQL. Recreate the admin with `flask create-admin`. For a demo, accept it and say so. |
| Free Render service sleeps, first request is slow, and WooCommerce webhooks may time out | Medium | Medium | Open the app a minute before demoing; WooCommerce retries failed deliveries; manual sync catches up. |
| Large store: sync inside one HTTP request may time out | Medium | Medium | Sync commits per page, so re-running continues the work. Next step: run sync in a background worker. |
| No WooCommerce test store available | Medium | High | `flask seed-demo` fills the UI with realistic data; payload tests prove the sync logic. |
| Webhook endpoint is public | Medium | High | HMAC signature verification; reject if no secret is set; constant-time compare. |
| JWT in `localStorage` (XSS) | Low | Medium | React escapes output by default; no `dangerouslySetInnerHTML`. Move to httpOnly cookies later. |
| Login brute force | Medium | Medium | Add rate limiting (Flask-Limiter) before production. |
| `localhost` WooCommerce over HTTP rejects Basic auth | Medium | Low | Client switches to query-string keys for `http://` stores. |
| WooCommerce data quirks (guest orders, deleted products, missing emails) | High | Low | Guest customers by email; product link optional; customer optional on orders. All covered by tests. |
| SQLite lock when sync and webhook overlap | Low | Low | 30-second busy timeout configured. |

## Known limitations (be upfront about these in a demo)
- Verified against realistic *mock payloads* and a seeded database, not against a live store from this build environment. Test against your own store before presenting.
- The frontend was build- and lint-checked; automated UI tests are not included.
- Single admin role, no password reset or change-password screen (use `flask create-admin` to reset).
- Deleted WooCommerce orders/customers are not removed from the CRM.
- Webhook "delete" topics are ignored on purpose.

## Future scope
1. **AI features** (originally planned): customer summaries, follow-up suggestions, email drafts. Add `ai_service.py` plus `/api/ai/*` routes using the Gemini API; the data they need is already exposed by `customer_service`.
2. PostgreSQL + Alembic migrations.
3. Background jobs (RQ/Celery) for sync; scheduled nightly reconciliation.
4. Email sending and templates; communication log per customer.
5. Roles and multiple admins; password reset; token blocklist; rate limiting.
6. Segments builder, tags, CSV export.
7. Multi-store support.
8. Frontend tests (Vitest + Testing Library) and end-to-end tests (Playwright); CI on GitHub Actions.
