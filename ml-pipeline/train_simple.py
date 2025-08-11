#!/usr/bin/env python3
"""
Simplified training script for ensemble model without MLflow
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import joblib
import os
import json
from datetime import datetime

# Create sample data for training
np.random.seed(42)
n_samples = 5000

# Generate synthetic property data
data = {
    'square_feet': np.random.uniform(1000, 50000, n_samples),
    'building_age': np.random.uniform(0, 100, n_samples),
    'num_floors': np.random.randint(1, 50, n_samples),
    'occupancy_rate': np.random.uniform(0.5, 1.0, n_samples),
    'walk_score': np.random.randint(20, 100, n_samples),
    'transit_score': np.random.randint(10, 100, n_samples),
    'crime_rate': np.random.uniform(0, 10, n_samples),
    'school_rating': np.random.uniform(3, 10, n_samples),
    'distance_to_downtown': np.random.uniform(0, 30, n_samples),
    'annual_revenue': np.random.uniform(50000, 5000000, n_samples),
    'expenses': np.random.uniform(20000, 2000000, n_samples),
    'cap_rate': np.random.uniform(0.04, 0.12, n_samples),
}

df = pd.DataFrame(data)

# Calculate NOI and property value
df['net_operating_income'] = df['annual_revenue'] - df['expenses']
df['property_value'] = np.abs(df['net_operating_income'] / df['cap_rate'])

# Add some noise
df['property_value'] += np.random.normal(0, np.abs(df['property_value']) * 0.1)

# Features and target
feature_cols = ['square_feet', 'building_age', 'num_floors', 'occupancy_rate',
                'walk_score', 'transit_score', 'crime_rate', 'school_rating',
                'distance_to_downtown', 'annual_revenue', 'expenses', 'cap_rate',
                'net_operating_income']

X = df[feature_cols]
y = df['property_value']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Training Property Valuation Models...")
print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

# Train XGBoost
print("\n1. Training XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=8,
    learning_rate=0.1,
    random_state=42
)
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

# Train LightGBM
print("2. Training LightGBM...")
lgb_model = lgb.LGBMRegressor(
    n_estimators=100,
    max_depth=8,
    learning_rate=0.1,
    random_state=42,
    verbosity=-1
)
lgb_model.fit(X_train, y_train)
lgb_pred = lgb_model.predict(X_test)

# Ensemble predictions (simple average)
ensemble_pred = (xgb_pred + lgb_pred) / 2

# Calculate metrics
def calculate_metrics(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    print(f"\n{model_name} Performance:")
    print(f"  MAE: ${mae:,.2f}")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  R²: {r2:.4f}")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  Accuracy: {(1 - mape/100)*100:.2f}%")
    
    return {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape, "accuracy": (1 - mape/100)*100}

# Evaluate models
xgb_metrics = calculate_metrics(y_test, xgb_pred, "XGBoost")
lgb_metrics = calculate_metrics(y_test, lgb_pred, "LightGBM")
ensemble_metrics = calculate_metrics(y_test, ensemble_pred, "Ensemble")

# Save models
os.makedirs('models', exist_ok=True)

print("\n" + "="*50)
print("Saving trained models...")

# Save models
joblib.dump(xgb_model, 'models/xgboost_model.pkl')
joblib.dump(lgb_model, 'models/lightgbm_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

# Save model metadata
metadata = {
    "training_date": datetime.now().isoformat(),
    "n_samples": n_samples,
    "features": feature_cols,
    "models": {
        "xgboost": xgb_metrics,
        "lightgbm": lgb_metrics,
        "ensemble": ensemble_metrics
    }
}

with open('models/model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("\nModels saved to 'models/' directory:")
print("  - xgboost_model.pkl")
print("  - lightgbm_model.pkl")
print("  - scaler.pkl")
print("  - model_metadata.json")

print("\n" + "="*50)
print("Training Complete!")
print(f"Final Ensemble Accuracy: {ensemble_metrics['accuracy']:.2f}%")
print("="*50)