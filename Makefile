VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

install: $(VENV_DIR)

black: $(VENV_DIR)
	$(ACTIVATE_VENV) && black .

ruff: $(VENV_DIR)
	$(ACTIVATE_VENV) && ruff check .

test: black ruff

#
# Docker commands
#

DOCKER_NETWORK=pizza_bot_network
POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_db
BOT_IMAGE=olgakotleta/pizza_bot
BOT_CONTAINER=pizza_bot

include .env
export $(shell sed 's/=.*//' .env)

# Initialize Buildx
buildx-setup:
	docker buildx create --name multiarch --use || true
	docker buildx inspect --bootstrap

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume docker_net
	docker run -d \
	  --name $(POSTGRES_CONTAINER) \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DB="$(POSTGRES_DATABASE)" \
	  -p "$(POSTGRES_PORT):$(POSTGRES_CONTAINER_PORT)" \
	  -v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
	  --health-cmd="pg_isready -U $(POSTGRES_USER)" \
	  --health-interval=10s \
	  --health-timeout=5s \
	  --health-retries=5 \
	  --network $(DOCKER_NETWORK) \
	  postgres:17

postgres_stop:
	docker stop $(POSTGRES_CONTAINER) || true
	docker rm $(POSTGRES_CONTAINER) || true

build:
	docker buildx build \
	  --platform linux/amd64,linux/arm64 \
	  -t $(BOT_IMAGE) \
	  -f Dockerfile \
	  --push .

build-dev:
	docker build \
	  -t $(BOT_IMAGE) \
	  -f Dockerfile .

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	  -e POSTGRES_PORT="$(POSTGRES_CONTAINER_PORT)" \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DATABASE="$(POSTGRES_DATABASE)" \
	  -e TOKEN="$(TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER) || true
	docker rm $(BOT_CONTAINER) || true

logs:
	docker logs -f $(BOT_CONTAINER)

clean: stop postgres-stop
	docker rmi $(BOT_IMAGE) || true

clean-all: clean
	docker system prune -f
	docker volume rm $(POSTGRES_VOLUME) || true

status:
	@echo "=== Containers ==="
	docker ps -a
	@echo "=== Images ==="
	docker images | grep $(BOT_IMAGE) || true
	@echo "=== Buildx ==="
	docker buildx ls

deploy: build push
	@echo "✅ Multi-platform image built and pushed to Docker Hub"