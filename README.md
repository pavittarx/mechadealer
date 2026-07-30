# mechadealer

mechadealer is a FinTech application that empowers retail investors to invest in
automated trading strategies. It allows users to view key performance metrics of each
strategy, monitor performance and adjust investments in real-time.

For a deep dive please read the docs [here](./docs/README.md).

## Live demo

**https://mechadealer-web.vercel.app** — sign in with `demo` / `demo1234`.

The frontend and API run on Vercel against a Neon Postgres database. The demo covers
authentication, the strategy views and the invest/withdraw flows. It deliberately does
not run the event pipeline — no Kafka, no QuestDB, no market data — so P&L stays at
zero. [Deployment](./docs/deployment.md) has the details and the rest of the caveats.

## Quickstart

Everything runs from the repository root. You never need to `cd` into a service
directory.

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `JWT_SECRET` (generate one with `openssl rand -hex 32`) and, if you want live
market data, your Upstox credentials. Then start the infrastructure:

```bash
uv run poe up
```

```bash
uv run poe api
```

```bash
uv run poe web
```

The API is on http://localhost:8000, the frontend on http://localhost:3000.

## Tasks

`uv run poe` lists them all. The useful ones:

| Task | What it does |
| --- | --- |
| `poe up` / `poe down` | Start / stop the infrastructure containers |
| `poe logs` | Tail the container logs |
| `poe api` | FastAPI application server (port 8000) |
| `poe web` | Nuxt frontend (port 3000) |
| `poe datasync` | Market data ingestion |
| `poe orders` | Order management |
| `poe stats` | Trade statistics |
| `poe strategy` | Run `strategy_0` |
| `poe check` | Lint, type-check and test |

To run the application services in containers as well:

```bash
docker compose --env-file .env -f containers/docker-compose.yaml --profile services up -d
```

`--env-file` matters: compose resolves `${VAR}` against a `.env` next to the compose
file, not against the repository root.

## Technology stack

Python 3.12+, FastAPI, Kafka, QuestDB, Postgres, Nuxt 4. Managed as a uv workspace.

## Layout

```
libs/          shared libraries, each a src-layout package
  coreutils      logging, scheduling, encrypted credential storage
  datastore      QuestDB access (time-series market data)
  storelib       Postgres access (users, strategies, orders)
  kafkalib       Kafka topics and event models
  brokerlib      broker integration (Upstox)
  strategylib    strategy runtime
projects/      runnable services, each a src-layout package
  app_server         FastAPI backend
  datasync           fetches market data, publishes to Kafka
  orders_management  consumes signals, places orders
  stats_handler      computes realised / unrealised P&L
  strategy_0         an EMA crossover strategy
app/           Nuxt frontend
containers/    Dockerfile and docker-compose stack
tests/         test suite (runs without infrastructure)
```

Data flow: `datasync` writes bars to QuestDB and publishes them to Kafka. A strategy
consumes bars and emits signals to the `signals` topic. `orders_management` consumes
signals and places orders through the broker. `stats_handler` computes P&L from filled
orders. `app_server` serves the frontend from Postgres.

## Ports

Every host port can be overridden in `.env` if something already holds it:

| Service | Default | Variable |
| --- | --- | --- |
| app_server | 8000 | `API_PORT` |
| QuestDB console | 9000 | `QDB_HTTP_PORT` |
| QuestDB PGWire | 8812 | `QDB_PG_PORT` |
| Postgres | 5432 | `PG_PORT` |
| Kafka | 9092 | `KAFKA_PORT` |
| Kafdrop | 9001 | `KAFDROP_PORT` |

## Runtime state

Encrypted broker credentials and log files are written under `~/.mechadealer` by
default; override with `MECHADEALER_HOME`. They were previously written to `.creds` and
`.logs` relative to the working directory, so each service saw a different set depending
on where it had been started.

## Conventions

- Libraries read configuration when a resource is first used, never at import time.
  Importing any library or service must work with no environment variables set and
  nothing running — `tests/test_packaging.py` enforces this.
- Services call `load_dotenv()`; libraries only read the environment.
- Every package uses a `src/` layout, so what you import is what a built wheel installs.
  `tests/test_packaging.py` and the `wheels` CI job guard this.

## Development

```bash
uv run poe check
```

Python 3.12 and 3.13 are verified in CI. Dependency resolution carries no upper bound and
no platform restriction.

Python 3.14 does not work yet, for a reason outside this repository: `quixstreams` caps
`confluent-kafka<2.12`, and the newest release in that range ships wheels only up to
cp313. `confluent-kafka` 2.15 has cp314 wheels, so this resolves itself once `quixstreams`
widens its constraint. No upper bound is declared here because the incompatibility is a
missing wheel rather than a real conflict.

### Indicators

`strategy_0` uses [`pandas-ta-classic`](https://pypi.org/project/pandas-ta-classic/)
rather than `pandas-ta`. The latter hard-pins `numba==0.61.2`, which caps numpy below 2.3
and holds pandas on 2.x, and it pulled a compiled toolchain into every image for a single
EMA call. `pandas-ta-classic` exposes the same API with numba as an optional extra.
`tests/test_indicators.py` pins EMA values captured from `pandas-ta` before the swap, so
a change in indicator output fails the build rather than quietly altering signals.
