#!/bin/bash

# Train ML models
echo "Starting ML model training..."

cd ml-pipeline

echo "Training ensemble models (XGBoost, LightGBM, Neural Network)..."
python3 train_ensemble.py

echo "Model training complete!"
echo "Models saved to mlflow and models/ directory"