FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked --no-dev
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
