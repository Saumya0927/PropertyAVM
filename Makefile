.PHONY: help setup run stop clean test build deploy generate-data train-models

help: ## Show this help message
	@echo "Property Valuation Model - Available Commands"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - install dependencies and generate data
	@echo "🚀 Setting up Property Valuation Model..."
	chmod +x scripts/setup.sh
	./scripts/setup.sh

run: ## Start all services with Docker Compose
	@echo "🐳 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   MLflow: http://localhost:5000"
	@echo "   Grafana: http://localhost:3001"

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped"

restart: stop run ## Restart all services

logs: ## View logs for all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs  
	docker-compose logs -f frontend

build: ## Build Docker images
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "✅ Build complete"

generate-data: ## Generate synthetic property data
	@echo "📊 Generating synthetic data..."
	cd data-generator && python generate_synthetic_data.py
	@echo "✅ Data generation complete"

train-models: ## Train ML models
	@echo "🤖 Training ML models..."
	cd ml-pipeline && python train_ensemble.py
	@echo "✅ Model training complete"

test: ## Run all tests
	@echo "🧪 Running tests..."
	@echo "Testing backend..."
	cd backend && python -m pytest tests/ -v
	@echo "Testing frontend..."
	cd frontend && npm test -- --watchAll=false
	@echo "✅ All tests complete"

test-backend: ## Run backend tests
	cd backend && python -m pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm test -- --watchAll=false

test-ml: ## Test ML pipeline
	cd ml-pipeline && python -c "from train_ensemble import PropertyValuationEnsemble; print('ML pipeline OK')"

lint: ## Run linters
	@echo "🔍 Running linters..."
	cd backend && python -m black . --check
	cd backend && python -m flake8 .
	cd frontend && npm run lint
	@echo "✅ Linting complete"

format: ## Format code
	@echo "🎨 Formatting code..."
	cd backend && python -m black .
	cd frontend && npm run format
	@echo "✅ Formatting complete"

clean: ## Clean up generated files and containers
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	rm -rf data/*.csv data/*.json
	rm -rf ml-pipeline/models/*
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/node_modules frontend/.next
	@echo "✅ Cleanup complete"

shell-backend: ## Open shell in backend container
	docker exec -it avm-backend /bin/bash

shell-postgres: ## Open PostgreSQL shell
	docker exec -it avm-postgres psql -U avm_user -d property_valuation

shell-redis: ## Open Redis CLI
	docker exec -it avm-redis redis-cli

health: ## Check service health
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not ready"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend: ✅ Healthy" || echo "Frontend: ❌ Not ready"
	@curl -s http://localhost:5000 > /dev/null && echo "MLflow: ✅ Healthy" || echo "MLflow: ❌ Not ready"
	@curl -s http://localhost:3001 > /dev/null && echo "Grafana: ✅ Healthy" || echo "Grafana: ❌ Not ready"

predict: ## Make a test prediction
	@echo "🔮 Making test prediction..."
	@curl -X POST http://localhost:8000/api/v1/valuations/predict \
		-H "Content-Type: application/json" \
		-d '{"square_feet": 10000, "property_type": "Office", "city": "New York", "occupancy_rate": 0.95, "num_floors": 3, "annual_revenue": 350000, "annual_expenses": 105000, "net_operating_income": 245000, "cap_rate": 0.06, "walk_score": 85, "transit_score": 90, "building_age": 10}' \
		| python -m json.tool

deploy-lambda: ## Deploy Lambda functions to LocalStack
	@echo "⚡ Deploying Lambda functions to LocalStack..."
	cd lambda-functions && \
	zip -r function.zip valuation_handler.py && \
	aws --endpoint-url=http://localhost:4566 lambda create-function \
		--function-name property-valuation \
		--runtime python3.9 \
		--role arn:aws:iam::000000000000:role/lambda-role \
		--handler valuation_handler.lambda_handler \
		--zip-file fileb://function.zip \
		--environment Variables={MODEL_BUCKET=avm-models,CACHE_TABLE=valuation-cache} \
		|| echo "Lambda already exists"
	@echo "✅ Lambda deployment complete"

monitor: ## Open monitoring dashboards
	@echo "📊 Opening monitoring dashboards..."
	@echo "Opening Grafana..."
	@open http://localhost:3001 2>/dev/null || xdg-open http://localhost:3001 2>/dev/null || echo "Visit http://localhost:3001"
	@echo "Opening MLflow..."
	@open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null || echo "Visit http://localhost:5000"

dev: ## Start development environment
	@echo "💻 Starting development environment..."
	$(MAKE) run
	@echo "Waiting for services to be ready..."
	@sleep 10
	$(MAKE) health
	@echo "✅ Development environment ready!"

prod: ## Build for production
	@echo "📦 Building for production..."
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Production build complete"

backup: ## Backup database
	@echo "💾 Backing up database..."
	@mkdir -p backups
	docker exec avm-postgres pg_dump -U avm_user property_valuation > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup complete"

restore: ## Restore database from latest backup
	@echo "♻️ Restoring database..."
	@latest_backup=$$(ls -t backups/*.sql | head -1); \
	if [ -z "$$latest_backup" ]; then \
		echo "No backup found"; \
	else \
		docker exec -i avm-postgres psql -U avm_user property_valuation < $$latest_backup; \
		echo "✅ Restored from $$latest_backup"; \
	fi