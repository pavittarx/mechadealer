FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  gcc \
  && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./

COPY libs ./libs/
COPY projects/datasync ./projects/datasync/

WORKDIR /app/projects/datasync
RUN uv sync
CMD ["uv", "run", "main.py"]