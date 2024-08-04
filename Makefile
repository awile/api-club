check: format lint typecheck

lint:
	ruff check app

typecheck:
	mypy app

format:
	black app

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f
