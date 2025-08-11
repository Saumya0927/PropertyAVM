#!/bin/bash

echo "🚀 Property Valuation Model - Quick Start"
echo "========================================="

# Use python3 explicitly
export PYTHON_CMD=python3

echo ""
echo "✅ Python packages installed successfully!"
echo ""
echo "📊 Step 1: Generating synthetic data..."
cd data-generator
$PYTHON_CMD generate_synthetic_data.py

echo ""
echo "🤖 Step 2: Training ML models..."
cd ../ml-pipeline
$PYTHON_CMD train_ensemble.py

echo ""
echo "🐳 Step 3: Starting Docker services..."
cd ..
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Access the application at:"
echo "  • Frontend: http://localhost:3000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • MLflow: http://localhost:5000"
echo "  • Grafana: http://localhost:3001"