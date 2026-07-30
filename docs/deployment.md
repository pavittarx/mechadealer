# Deployment

A live demo of the interface runs at **https://mechadealer-web.vercel.app**
(`demo` / `demo1234`).

The demo exists to show the UI and the API against real data. It is not the full
system: the event pipeline is deliberately absent. See [What the demo does not
run](#what-the-demo-does-not-run).

## Shape

```
mechadealer-web  ──HTTPS──>  mechadealer-api  ──TLS──>  Neon Postgres
(Nuxt, static)               (FastAPI, ASGI function)   (mechadealer-demo)
```

Three pieces, all on free tiers:

| Piece | Where | Production URL |
| --- | --- | --- |
| Frontend | Vercel project `mechadealer-web` | https://mechadealer-web.vercel.app |
| API | Vercel project `mechadealer-api` | https://mechadealer-api.vercel.app |
| Database | Neon `mechadealer-demo` (`shiny-pine-40285992`) | Postgres 17, `aws-us-east-1` |

Both Vercel projects live under the `portal-7254s-projects` scope.

The API has no route at `/`, so a bare request to the API host returns 404. That is
expected. `GET /health` is the liveness endpoint:

```bash
curl https://mechadealer-api.vercel.app/health
```

## How the API is packaged

Vercel serves FastAPI as a single ASGI function. Three files make that work, and each
one exists to solve a specific problem:

`api/index.py` is the entrypoint. Vercel discovers `app` in it and serves it. It only
re-exports `app_server.main:app` — the packages are installed normally, so no `sys.path`
manipulation is needed.

`requirements.txt` installs the two workspace members the function actually needs.
pip does not understand uv workspaces, so the members are listed as local paths, and
**order matters** — `storelib` is installed first so that `app_server`'s dependency on it
is already satisfied and pip does not try to resolve the name against PyPI.

`.vercelignore` excludes everything the function does not need, and one entry is
load-bearing beyond size: `/pyproject.toml`. Vercel's Python builder prefers `uv lock`
when it finds a root `pyproject.toml`, which fails here because `tool.uv.sources`
references workspace members this deployment deliberately excludes. Hiding the root
manifest forces the pip path declared in `vercel.json`. The leading slash matters — it
hides only the root file, so the member manifests under `libs/` and `projects/` are
still uploaded.

## Environment

Set in the Vercel dashboard, not in the repository.

`mechadealer-api`:

| Variable | Purpose |
| --- | --- |
| `PG_CONNECTION_STRING` | Neon pooled connection string |
| `JWT_SECRET` | Signs session tokens |
| `CORS_ORIGINS` | Comma-separated allowed origins; the frontend URL |
| `INIT_DB_ON_STARTUP` | Set to `false` in production — see below |

`mechadealer-web`:

| Variable | Purpose |
| --- | --- |
| `NUXT_PUBLIC_BASE_URL` | API base URL the browser calls |

`INIT_DB_ON_STARTUP` defaults to **on**, which is what you want locally against an empty
database and the wrong thing in production: `init_db()` runs `create_all`, so leaving it
on repeats that work on every cold start of a serverless function without ever being
able to alter an existing table. Turn it off once the schema exists and let migrations
carry schema changes instead.

Vercel stores these encrypted and does not read them back, so the values above cannot be
verified from the CLI — only overwritten. `CORS_ORIGINS` is the exception, because its
effect is observable:

```bash
# allowed origin -> 200 with access-control-allow-origin
curl -si -X OPTIONS https://mechadealer-api.vercel.app/login \
  -H 'Origin: https://mechadealer-web.vercel.app' \
  -H 'Access-Control-Request-Method: POST' | grep -i '^access-control-allow-origin'
```

Any other origin gets a 400 with no `access-control-allow-origin` header.

## Migrations

`create_all` creates missing tables but never alters an existing one, so it cannot carry
a column change to a database that already holds data. Numbered SQL under `migrations/`
does that. Each file is applied once, in its own transaction, and recorded in
`schema_migrations`.

```bash
PG_CONNECTION_STRING='<neon-connection-string>' uv run poe migrate
```

Re-running is a no-op — it reports `no pending migrations`. Migrations are forward-only;
there are no down-scripts. To reverse something, write the next migration.

Apply migrations **before** deploying code that depends on the new schema.

## Deploying

Vercel git integration is not connected, so deploys are CLI-only and manual. A push to
GitHub does not deploy anything.

```bash
vercel --prod
```

for the API, from the repository root, and the same command from `app/` for the
frontend. CI (lint, type-check, tests, wheel builds) runs on GitHub Actions and gates
the pull request, but it does not deploy.

## What the demo does not run

Kafka, QuestDB, `datasync`, `orders_management`, `stats_handler` and `strategy_0` are
all absent. The demo is the frontend, the API and Postgres — enough to exercise
authentication, the strategy views and the invest/withdraw flows, which is what the
demo is for. Running the pipeline needs long-lived stateful services, which serverless
functions are the wrong shape for.

Consequences worth knowing before reading the numbers on screen:

- **No market data and no orders.** P&L stays at zero because nothing fills.
- **`capital_used` is always zero.** Nothing increments it on a fill — that accounting
  is not implemented — so "Deployed" reads ₹0.00 and the order balance gate checks
  against the whole pool rather than free capital. This is a gap in the application, not
  in the deployment.
- **Cold starts.** Both the function and the Neon compute suspend when idle, so the
  first request after a quiet period is slow.
- **Shared demo state.** One seeded account, no isolation between visitors. Anyone can
  move its money around.
