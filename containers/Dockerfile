# One image for every Python service. Which service runs is decided by the
# `command:` in docker-compose.yaml, so there is a single build to maintain
# instead of one Dockerfile per project.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc curl \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependency layer: only the manifests, so edits to source do not invalidate it.
COPY pyproject.toml uv.lock ./
COPY libs/coreutils/pyproject.toml libs/coreutils/
COPY libs/datastore/pyproject.toml libs/datastore/
COPY libs/kafkalib/pyproject.toml libs/kafkalib/
COPY libs/storelib/pyproject.toml libs/storelib/
COPY libs/strategylib/pyproject.toml libs/strategylib/
COPY libs/brokerlib/pyproject.toml libs/brokerlib/
COPY projects/app_server/pyproject.toml projects/app_server/
COPY projects/datasync/pyproject.toml projects/datasync/
COPY projects/orders_management/pyproject.toml projects/orders_management/
COPY projects/stats_handler/pyproject.toml projects/stats_handler/
COPY projects/strategy_0/pyproject.toml projects/strategy_0/
RUN uv sync --frozen --no-dev --no-install-workspace

# Source layer.
COPY libs libs
COPY projects projects
RUN uv sync --frozen --no-dev

CMD ["datasync"]
