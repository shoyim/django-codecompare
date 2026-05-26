.PHONY: help install dev test lint format migrate run docker-build docker-up docker-down clean

help:
	@echo "codecompare development commands"
	@echo ""
	@echo "  install      Install production dependencies"
	@echo "  dev          Install dev dependencies"
	@echo "  test         Run test suite"
	@echo "  lint         Run ruff linter"
	@echo "  format       Auto-format with ruff"
	@echo "  migrate      Run Django migrations"
	@echo "  run          Start dev server"
	@echo "  docker-build Build Docker images"
	@echo "  docker-up    Start all services via docker-compose"
	@echo "  docker-down  Stop all services"
	@echo "  clean        Remove build artifacts"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -x --tb=short -q

test-cov:
	pytest tests/ --cov=codecompare --cov-report=html --cov-report=term-missing -q

test-bench:
	pytest tests/benchmarks/ --benchmark-only -v

lint:
	ruff check codecompare/ tests/

format:
	ruff format codecompare/ tests/
	ruff check --fix codecompare/ tests/

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

run:
	python manage.py runserver 0.0.0.0:8000

run-asgi:
	uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A config.celery worker -l info

docker-build:
	docker build -f docker/Dockerfile -t codecompare:latest .
	docker build -f docker/Dockerfile.worker -t codecompare-worker:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage coverage.xml dist build *.egg-info
