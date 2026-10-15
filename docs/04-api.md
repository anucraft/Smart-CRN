# 4. REST API

Base URL: `http://localhost:5000/api` (local) · all responses are JSON · protected endpoints need `Authorization: Bearer <token>`.

**Errors** always look like `{"error": "Human readable message"}` with a suitable status (400 bad input, 401 not authenticated, 404 missing, 503 not configured).

**Pagination** (list endpoints): query `page` (default 1) and `per_page` (default 10, max 100). Response: `{items, page, per_page, total, pages}`.

## Authentication
| Endpoint | Method | Auth | Purpose | Request | Response |
|----------|--------|------|---------|---------|----------|
| `/auth/login` | POST | No | Exchange credentials for a token | `{email, password}` | `200 {access_token, admin}` · `400` missing fields · `401` wrong credentials |
| `/auth/me` | GET | Yes | Who am I? (validates a stored token on page load) | – | `200 {admin:{id,email,name}}` |

There is no `/auth/logout`: JWTs are stateless, so logging out deletes the token in the browser.

## Customers
| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/customers` | GET | List with search, filter, sort | `q`, `segment` (vip/returning/new/prospect), `sort` (newest/spent/orders/name), `page`, `per_page` | Paginated customers, each with `orders_count`, `total_spent`, `last_order_at`, `segment` |
| `/customers/{id}` | GET | Profile + stats + 10 latest orders | – | Customer fields + stats + `recent_orders[]` · `404` |
| `/customers/{id}/timeline` | GET | Activity feed for one customer | – | `{items:[{id,type,description,created_at}]}` |
| `/customers/{id}/notes` | GET | List notes (newest first) | – | `{items:[{id,body,author,created_at}]}` |
| `/customers/{id}/notes` | POST | Add a note | `{body}` (1 to 2000 chars) | `201` the note · `400` empty/too long |
| `/customers/{id}/notes/{noteId}` | DELETE | Delete a note | – | `204` · `404` |

Customers are read-only here on purpose: WooCommerce is the source of truth, and an edit made in the CRM would be overwritten by the next sync.

## Orders
| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/orders` | GET | List/search orders | `q` (number, customer name/email), `status`, `page`, `per_page` | Paginated orders with `payment_status`, `shipping_status`, `customer` |
| `/orders/{id}` | GET | Full order | – | Order + `items[]`, `billing`, `shipping`, tax/shipping/discount, dates · `404` |

## Products
| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/products` | GET | List/search catalogue | `q` (name/SKU), `page`, `per_page` | Paginated products |

## Analytics
| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/analytics/summary` | GET | Dashboard numbers | – | `{total_customers,total_orders,revenue,pending_orders,average_order_value}` |
| `/analytics/monthly-sales` | GET | Revenue + orders per month (zero-filled) | `months` (1-24, default 12) | `{items:[{month:"2026-09",revenue,orders}]}` |
| `/analytics/customer-growth` | GET | New and cumulative customers | `months` | `{items:[{month,new_customers,total_customers}]}` |
| `/analytics/top-customers` | GET | Biggest spenders | `limit` (1-20, default 5) | `{items:[{id,name,email,total_spent,orders_count}]}` |
| `/analytics/recent-activity` | GET | Latest events | `limit` (1-50, default 10) | `{items:[{id,type,description,customer_name,created_at}]}` |

## WooCommerce
| Endpoint | Method | Auth | Purpose | Request | Response |
|----------|--------|------|---------|---------|----------|
| `/woocommerce/status` | GET | Yes | Is it configured? When did we last sync? Row counts | – | `{configured,last_sync,counts:{customers,orders,products}}` |
| `/woocommerce/test-connection` | POST | Yes | Verify store URL and keys | – | `200 {ok,message}` · `400 {error}` with the reason |
| `/woocommerce/sync/{resource}` | POST | Yes | Pull data. `resource` = `all`, `customers`, `orders` or `products` | – | `{finished_at,results:{orders:{created,updated,total}}}` · `400` not configured/rejected · `404` unknown resource |
| `/woocommerce/webhook` | POST | **Signature** | Receive WooCommerce events | Raw WooCommerce JSON; headers `X-WC-Webhook-Signature`, `X-WC-Webhook-Topic` | `200 {status: processed/ignored/pong}` · `401` bad signature · `503` no secret saved |

## Settings
| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/settings` | GET | Current WooCommerce config (secrets hidden) | – | `{store_url, consumer_key (masked), has_consumer_secret, has_webhook_secret, webhook_url, configured}` |
| `/settings` | PUT | Save config. Blank secrets keep the stored value | `{store_url?, consumer_key?, consumer_secret?, webhook_secret?}` | Same as GET · `400` bad URL |

## Utility
`GET /api/health` is public and returns `{"status":"ok"}`. Render uses it as the health check.

## Sample exchange
```http
POST /api/auth/login
{"email":"demo@smartcrm.dev","password":"demo1234"}

200 {"access_token":"eyJ...","admin":{"id":1,"email":"demo@smartcrm.dev","name":"Demo"}}
```
```http
GET /api/customers?segment=vip&sort=spent&per_page=1
Authorization: Bearer eyJ...

200 {"items":[{"id":20,"name":"Anika Rossi","email":"anika.rossi19@example.com","orders_count":3,
      "total_spent":691.0,"segment":"vip","city":"Austin","country":"US", "...": "..."}],
     "page":1,"per_page":1,"total":9,"pages":9}
```
