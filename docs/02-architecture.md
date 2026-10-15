# 2. Architecture

## Layered architecture
Each layer talks only to the one below it. This keeps HTTP concerns out of business logic and makes each layer testable.

```mermaid
flowchart TD
    UI["React SPA (Vercel)<br/>pages, components, Axios"] -->|"HTTPS + JSON, JWT header"| API
    WC["WooCommerce store"] -->|"Webhook POST + HMAC signature"| API
    subgraph Backend["Flask backend (Render)"]
        API["Routes (blueprints)<br/>parse request, validate, return JSON"] --> SVC["Service layer<br/>business rules, sync, analytics"]
        SVC --> ORM["SQLAlchemy models"]
        SVC --> WCC["WooClient<br/>HTTP wrapper"]
    end
    ORM --> DB[("SQLite file")]
    WCC -->|"REST API v3"| WC
```

| Layer | Folder | Responsibility | Must NOT |
|-------|--------|----------------|----------|
| Routes | `app/routes` | Read request, check input, call a service, shape the response | Contain business rules or SQL |
| Services | `app/services` | Business rules: sync, segments, analytics, webhook handling | Read Flask `request` objects; they receive plain values from routes |
| Models | `app/models` | Table definitions, relationships, small derived properties | Call external APIs |
| WooClient | `app/services/woo_client.py` | All HTTP to WooCommerce | Touch the database |

Dependencies point downward only: routes → services → models/WooClient. Because `woo_sync_service` receives a *client object*, tests pass a `FakeWooClient` and never touch the network.

## Request flow (a normal page load)
```mermaid
sequenceDiagram
    participant B as Browser (React)
    participant A as Axios interceptor
    participant R as Route /api/customers
    participant S as customer_service
    participant D as SQLite
    B->>A: customersApi.list({q, page})
    A->>R: GET /api/customers?q=maya (Authorization: Bearer JWT)
    R->>R: jwt_required verifies token
    R->>S: list_customers_query(q, segment, sort)
    S->>D: one SELECT with an order-stats subquery
    D-->>S: rows
    S-->>R: (Customer, orders_count, total_spent, last_order_at)
    R-->>B: {items, page, pages, total}
```

## Authentication flow
```mermaid
sequenceDiagram
    participant B as Browser
    participant API as Flask
    B->>API: POST /api/auth/login {email, password}
    API->>API: look up admin, check_password_hash
    API-->>B: 200 {access_token, admin}   (401 on failure)
    B->>B: store token in localStorage
    B->>API: GET /api/... + Authorization: Bearer token
    API-->>B: 200 data
    Note over B,API: Token expires (default 12h) -> API returns 401 -> Axios interceptor clears token -> ProtectedRoute redirects to /login
    B->>B: Logout = delete token (JWTs are stateless)
```
**Trade-off:** `localStorage` is simple but readable by any script running on the page (XSS risk). For production consider an httpOnly cookie plus CSRF protection. **Logout** only removes the token client-side; a stolen token stays valid until it expires. A server-side blocklist is listed in the roadmap.

## WooCommerce sync flow (manual button)
```mermaid
sequenceDiagram
    participant UI as Settings / Sync button
    participant R as POST /api/woocommerce/sync/all
    participant SY as woo_sync_service
    participant C as WooClient
    participant WC as WooCommerce
    UI->>R: click "Sync WooCommerce"
    R->>C: build client from saved credentials
    loop products, then customers, then orders
        SY->>C: pages(resource)
        C->>WC: GET /wp-json/wc/v3/{resource}?per_page=100&page=n
        WC-->>C: JSON page + X-WP-TotalPages
        SY->>SY: upsert each record (insert or update)
        SY->>SY: commit this page
    end
    SY->>SY: log activity + save last_sync
    R-->>UI: {finished_at, results:{products:{created,updated,total},...}}
```
Order matters: products first (so order lines can link to products), customers second, orders last.

## Webhook flow (real time)
```mermaid
sequenceDiagram
    participant WC as WooCommerce
    participant W as POST /api/woocommerce/webhook
    participant V as webhook_service
    participant SY as woo_sync_service
    WC->>W: body + X-WC-Webhook-Signature + X-WC-Webhook-Topic
    W->>V: verify_signature(raw body, signature, secret)
    alt signature invalid or secret missing
        W-->>WC: 401 / 503
    else valid
        W->>V: handle_event(topic, payload)
        V->>SY: upsert_order / upsert_customer / upsert_product
        SY-->>V: row saved + activity logged
        W-->>WC: 200 {status: processed}
    end
```
Key points:
1. **The endpoint is public** (WooCommerce cannot send a JWT), so the HMAC signature is the only protection. We verify against the *raw bytes* of the body, using `hmac.compare_digest`.
2. **Idempotent.** WooCommerce may deliver the same event twice or out of order. Upserts make that harmless.
3. **Always answer fast.** WooCommerce disables a webhook after repeated failed deliveries, so we return 500 only on genuine processing errors.
4. `*.deleted` topics are ignored on purpose: a CRM should keep history.
5. The "ping" WooCommerce sends when you save a webhook is form-encoded; we answer `pong`.

## Where did AI go?
Removed from this build as requested. The service layer is the natural place to add it later (`ai_service.py` reading from `customer_service`), with no changes to existing code.
