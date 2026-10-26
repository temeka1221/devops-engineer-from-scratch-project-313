.PHONY: install run test lint format
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
