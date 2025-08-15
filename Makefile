format:
	ruff format .

lint:
	ruff check .

test:
	pytest

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

docker_full_run:
	docker compose up --build
	docker attach job-streamer



