# 6. Project structure and what every part is for

```text
smartcrm/
├── README.md                    Entry point: what it is, how to run it
├── .gitignore                   Keeps secrets, venvs, node_modules, db files out of Git
├── docs/                        All project documentation (you are here)
├── backend/
│   ├── wsgi.py                  Entry point for `flask` CLI and gunicorn
│   ├── .flaskenv                Tells `flask` which file is the app (FLASK_APP=wsgi.py)
│   ├── .env.example             Template of every environment variable (copy to .env)
│   ├── requirements.txt         Pinned runtime dependencies (deployed)
│   ├── requirements-dev.txt     Runtime + pytest
│   ├── app/
│   │   ├── __init__.py          create_app(): builds Flask, registers everything, JSON error handlers
│   │   ├── config.py            Config from environment (Config, TestConfig)
│   │   ├── extensions.py        db, jwt, cors objects (created unbound to avoid circular imports)
│   │   ├── cli.py               `flask create-admin`, `init-db`, `seed-demo`
│   │   ├── models/              One file per table concept
│   │   │   ├── admin.py         Admin + password hashing
│   │   │   ├── customer.py      Customer
│   │   │   ├── order.py         Order, OrderItem, revenue/open status constants, derived statuses
│   │   │   ├── product.py       Product
│   │   │   ├── activity.py      Activity (event log) and CustomerNote
│   │   │   └── setting.py       Key/value Setting
│   │   ├── routes/              HTTP layer: one blueprint per module
│   │   │   ├── auth.py          /api/auth/*
│   │   │   ├── customers.py     /api/customers/* (+ notes, timeline)
│   │   │   ├── orders.py        /api/orders/*
│   │   │   ├── products.py      /api/products
│   │   │   ├── analytics.py     /api/analytics/*
│   │   │   ├── woocommerce.py   /api/woocommerce/* (status, test, sync, webhook)
│   │   │   └── settings.py      /api/settings
│   │   ├── services/            Business logic
│   │   │   ├── woo_client.py        HTTP client for WooCommerce REST API (pagination, errors)
│   │   │   ├── woo_sync_service.py  Upserts + bulk sync (shared by sync button and webhooks)
│   │   │   ├── webhook_service.py   Signature check + topic dispatch
│   │   │   ├── customer_service.py  Customer list query with stats, segments, notes
│   │   │   ├── order_service.py     Order list query
│   │   │   ├── analytics_service.py Dashboard and chart numbers
│   │   │   ├── activity_service.py  Write/read the event log
│   │   │   └── settings_service.py  Read/write settings with env fallback, masking
│   │   └── utils/
│   │       ├── responses.py     error(), pagination helpers
│   │       └── time.py          UTC helpers, WooCommerce date parsing
│   └── tests/                   pytest suite (31 tests)
│       ├── conftest.py          App, client and logged-in-admin fixtures (in-memory DB)
│       ├── fixtures.py          Realistic WooCommerce payloads + FakeWooClient
│       └── test_*.py            Auth, sync, webhook, client, customers/orders/analytics/settings
└── frontend/
    ├── index.html               HTML shell, loads fonts
    ├── vite.config.js           Vite + React + Tailwind plugins
    ├── vercel.json              Rewrites all paths to index.html (SPA routing on Vercel)
    ├── .env.example             VITE_API_URL
    ├── package.json             Dependencies and scripts
    └── src/
        ├── main.jsx             Mounts React with Router, motion config, AuthProvider
        ├── App.jsx              Route table
        ├── index.css            Tailwind import, design tokens (@theme), shared component classes
        ├── api/                 client.js (Axios + interceptors) and index.js (one function per endpoint)
        ├── context/             AuthContext (login state, token handling)
        ├── hooks/               useFetch (load data), useDebounce (search input)
        ├── utils/format.js      Money, date and label formatting
        ├── components/          Layout, ProtectedRoute, SyncButton, ui.jsx (Badge, Pagination, states), charts/
        └── pages/               One file per screen
```

## Why this layout
- **Routes / services / models** separate "talking HTTP", "making decisions" and "storing data". A reviewer can find any rule in one obvious place.
- **`api/` on the frontend** means components never build URLs; changing an endpoint touches one file.
- **`tests/fixtures.py`** uses payloads shaped like real WooCommerce responses, so the sync logic is tested against realistic data without a store.
- **`docs/`** lives in the repo so documentation is versioned with the code.
- **No `assets/` folder:** the only asset is the favicon in `frontend/public`. An empty folder would be noise.
