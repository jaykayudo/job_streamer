format:
	ruff format .

lint:
	ruff check .

test:
	pytest

build:
	docker compose build

run:
	docker compose up

stop:
	docker compose down

clean:
	docker compose down
	docker compose rm -f
	docker compose build
	docker compose up

run_client:
	python -m bin.start



