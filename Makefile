.PHONY: dev build test migrate seed clean logs shell ps

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build:
	docker compose build

test:
	docker compose run --rm backend pytest tests/ -v --asyncio-mode=auto

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm backend python -m app.scripts.seed_metrics

logs:
	docker compose logs -f backend celery_worker

clean:
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

shell:
	docker compose run --rm backend python -m asyncio

ps:
	docker compose ps
