# Makefile
# For starting the docker compose services on a new machine.

# Variables
DOCKER_COMPOSE_VERSION = 27.5

# Install Docker
install-docker:
	@echo "Installing Docker..."
	@sudo apt update
	@sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
	@curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	@sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	@sudo apt update
	@sudo apt install -y docker-ce

# Install Docker Compose
install-docker-compose:
	@echo "Installing Docker Compose..."
	@sudo curl -L "https://github.com/docker/compose/releases/download/$(DOCKER_COMPOSE_VERSION)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	@sudo chmod +x /usr/local/bin/docker-compose

# Install Loki Plugin
install-loki:
	@echo "Checking for Loki plugin..."
	@if ! docker plugin ls | grep -q "loki"; then \
		echo "Installing Loki Docker plugin..."; \
		sudo docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions; \
	else \
		echo "Loki Docker plugin is already installed."; \
	fi

# Start Docker Compose
up: install-docker install-docker-compose install-loki
	@echo "Starting Docker Compose services..."
	@docker compose up -d

# Stop Docker Compose
down:
	@echo "Stopping Docker Compose services..."
	@docker compose down

# Clean up Docker system
clean:
	@echo "Cleaning up Docker system..."
	@docker system prune -af

# Full setup
setup: install-docker install-docker-compose install-loki up

.PHONY: install-docker install-docker-compose install-loki up down clean setup