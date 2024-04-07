.PHONY: run-dev-server
run-dev-server:
	ENV=development poetry run uvicorn app.main:app --workers 4 --proxy-headers --forwarded-allow-ips='*' --reload

.PHONY: migrate-dev-db
migrate-dev-db:
	ENV=development DB_URL=mysql+pymysql://root:1234567890@localhost:3306/glida_dev poetry run alembic --name server upgrade head

.PHONY: downgrade-dev-db
downgrade-dev-db:
	ENV=development DB_URL=mysql+pymysql://root:1234567890@localhost:3306/glida_dev poetry run alembic --name server downgrade -1

.PHONY: autogenerate-migration
autogenerate-migration:
	ENV=development poetry run alembic --name server revision --autogenerate -m "$(m)"

.PHONY: check-lint
check-lint:
	poetry run black app --target-version py38 --check
	poetry run flake8 --max-line-length 120 --ignore "E203, W503"
	poetry run isort --check .
	poetry run mypy app

.PHONY: lint
lint:
	poetry run black app --target-version py38
	poetry run flake8 --max-line-length 120 --ignore "E203, W503"
	poetry run isort .
	poetry run mypy app
