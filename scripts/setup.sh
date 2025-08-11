#!/bin/bash

set -e

echo "=================================================="
echo "Property Valuation Model - Setup Script"
echo "=================================================="

echo -e "\n📦 Creating necessary directories..."
mkdir -p data
mkdir -p ml-pipeline/models
mkdir -p infrastructure/localstack
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p monitoring/prometheus

echo -e "\n🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo -e "\n📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r data-generator/requirements.txt || pip install pandas numpy

echo -e "\n🏗️ Generating synthetic dataset..."
cd data-generator
python generate_synthetic_data.py
cd ..

echo -e "\n🤖 Training ML models..."
cd ml-pipeline
python train_ensemble.py
cd ..

echo -e "\n🐳 Building Docker images..."
docker-compose build

echo -e "\n🚀 Starting services..."
docker-compose up -d

echo -e "\n⏳ Waiting for services to be ready..."
sleep 10

echo -e "\n✅ Checking service health..."
curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not ready yet"

echo -e "\n📊 Creating database tables..."
docker exec avm-postgres psql -U avm_user -d property_valuation -c "
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(50) UNIQUE NOT NULL,
    property_type VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50),
    square_feet INTEGER,
    property_value DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS valuations (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(50),
    predicted_value DECIMAL(15, 2),
    confidence_lower DECIMAL(15, 2),
    confidence_upper DECIMAL(15, 2),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    accuracy DECIMAL(5, 2),
    rmse DECIMAL(15, 2),
    mae DECIMAL(15, 2),
    r2_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
" || echo "Database setup will complete when PostgreSQL is ready"

echo -e "\n=================================================="
echo "✨ Setup Complete!"
echo "=================================================="
echo ""
echo "🌐 Access the application at:"
echo "   • Frontend: http://localhost:3000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • MLflow UI: http://localhost:5000"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "📋 Next steps:"
echo "   1. Visit http://localhost:3000 to see the web interface"
echo "   2. Check API documentation at http://localhost:8000/docs"
echo "   3. View model experiments at http://localhost:5000"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f [service-name]"
echo ""
echo "=================================================="