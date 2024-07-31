check: format lint typecheck

lint:
	ruff check app

typecheck:
	mypy app


format:
	black app
