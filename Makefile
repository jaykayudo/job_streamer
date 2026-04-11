format:
	ruff format .

lint:
	ruff check .

test:
	pytest

# ── Database migrations (Alembic) ─────────────────────────────────────────────
migrate:
	poetry run python scripts/migrate.py upgrade

migrate-down:
	poetry run python scripts/migrate.py downgrade

migrate-revision:
	poetry run python scripts/migrate.py revision "$(msg)"

migrate-history:
	poetry run python scripts/migrate.py history

migrate-current:
	poetry run python scripts/migrate.py current

build:
	HOST=0.0.0.0 docker compose build

run:
	HOST=0.0.0.0 docker compose up

stop:
	docker compose down

clean:
	docker compose down
	docker compose rm -f
	HOST=0.0.0.0 docker compose build
	HOST=0.0.0.0 docker compose up

run_client:
	python -m bin.start

run_cli_client:
	poetry run python3 -m client.command_line.run

run_web_client:
	poetry run python3 -m client.web.run

docker_full_run:
	docker compose up --build
	docker attach job-streamer



