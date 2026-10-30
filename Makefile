.PHONY: install run lint format

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .