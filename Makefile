.PHONY: help install dev test lint clean build up down logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "All dependencies installed!"

dev: ## Start development servers (Docker)
	docker-compose -f docker-compose.dev.yml up

dev-build: ## Build and start development servers
	docker-compose -f docker-compose.dev.yml up --build

prod: ## Start production servers (Docker)
	docker-compose up -d

prod-build: ## Build and start production servers
	docker-compose up -d --build

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm run test

test-coverage: ## Run tests with coverage
	@echo "Running backend tests with coverage..."
	cd backend && pytest --cov=app --cov-report=term --cov-report=html
	@echo "Running frontend tests with coverage..."
	cd frontend && npm run test:coverage

lint: ## Run linters for both backend and frontend
	@echo "Linting backend..."
	cd backend && black --check . && flake8 . && mypy app
	@echo "Linting frontend..."
	cd frontend && npm run lint && npm run format:check

lint-fix: ## Fix linting issues
	@echo "Fixing backend formatting..."
	cd backend && black .
	@echo "Fixing frontend linting..."
	cd frontend && npm run lint:fix && npm run format

clean: ## Clean up temporary files and caches
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes
	docker-compose down -v

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

ps: ## Show running containers
	docker-compose ps

restart: ## Restart all services
	docker-compose restart

health: ## Check health of services
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/health || echo "Backend is not responding"
	@echo "\nChecking frontend health..."
	@curl -f http://localhost/health || echo "Frontend is not responding"
