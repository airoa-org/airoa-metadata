.PHONY: format lint ruff-fix ruff-check mypy test test-coverage

format: ruff-fix

ruff-fix:
	uv run ruff format airoa_metadata/
	uv run ruff check --fix airoa_metadata/

lint: ruff-check mypy

ruff-check:
	uv run ruff check airoa_metadata/
	uv run ruff format --check airoa_metadata/

mypy:
	uv run mypy airoa_metadata/

test:
	uv run pytest airoa_metadata/tests/ -svv

test-coverage:
	uv run pytest airoa_metadata/tests/ --cov=airoa_metadata/ --cov=airoa_metadata --cov-report=term-missing
