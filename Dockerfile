FROM node:26-slim AS ui
WORKDIR /ui
COPY package.json package-lock.json ./
RUN npm ci

FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked --no-dev
COPY . .
COPY --from=ui /ui/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/ ./public

ENV PATH="/app/.venv/bin:$PATH"
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
