.PHONY: install run test lint format frontend dev
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
	@npx start-hexlet-devops-deploy-crud-frontend --port

dev:
	@npx concurrently -k -n run,frontend -c blue,green "$(MAKE) run" "$(MAKE) frontend"