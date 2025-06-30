# Project Variables
IMAGE_NAME=chainlit-app
CONTAINER_NAME=chainlit_container
PORT=8000

# Compose files
COMPOSE_FILES=docker-compose.common.yml docker-compose.app.yml docker-compose.cache.yml
COMPOSE_ARGS=$(foreach file,$(COMPOSE_FILES),-f $(file))

# GPU flag for docker run
GPU_FLAG=--gpus all

# Default target
.PHONY: help
help:
	@echo "Makefile commands:"
	@echo "  build        - Build the Docker image(s)"
	@echo "  up           - Start all services"
	@echo "  down         - Stop and remove services"
	@echo "  restart      - Restart all services"
	@echo "  logs         - Show logs from the main app container"
	@echo "  bash         - Open shell inside app container"
	@echo "  run          - Run app container manually with GPU (bypass compose)"
	@echo "  clean        - Remove container and image"

# Build all services
.PHONY: build
build:
	docker compose $(COMPOSE_ARGS) build

# Start all services
.PHONY: up
up:
	docker compose $(COMPOSE_ARGS) up

# Stop all services
.PHONY: down
down:
	docker compose $(COMPOSE_ARGS) down

# Restart all services
.PHONY: restart
restart: down up

# Show logs from app
.PHONY: logs
logs:
	docker compose $(COMPOSE_ARGS) logs -f $(CONTAINER_NAME)

# Open shell in app container
.PHONY: bash
bash:
	docker exec -it $(CONTAINER_NAME) /bin/bash

# Run manually (standalone, GPU)
.PHONY: run
run:
	docker run --rm -it \
		$(GPU_FLAG) \
		--name $(CONTAINER_NAME) \
		-p $(PORT):8000 \
		-v $(PWD):/app \
		-w /app \
		$(IMAGE_NAME) \
		chainlit run app.py --host 0.0.0.0 --port 8000

# Clean everything
.PHONY: clean
clean:
	-docker rm -f $(CONTAINER_NAME)
	-docker rmi -f $(IMAGE_NAME)
