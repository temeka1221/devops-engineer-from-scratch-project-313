.PHONY: install run test lint format frontend dev build
install:
	@uv sync

run:
	@uv run uvicorn main:app --host 0.0.0.0 --port 8080

test:
	@uv run pytest

lint:
	@uv run ruff check .
	@uv run ruff format --check .

format:
	@uv run ruff format .
	@uv run ruff check --fix .

frontend:
	@npx start-hexlet-devops-deploy-crud-frontend

dev:
	@npx concurrently -k -n run,frontend -c blue,green "$(MAKE) run" "$(MAKE) frontend"

build:
	@uv sync
	@npm ci
	@rm -rf public
	@mkdir -p public
	@cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. public/