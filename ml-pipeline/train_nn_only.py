#!/usr/bin/env python3
"""
Train only the neural network component to complete the ensemble.
This script runs in the backend container with existing data.
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import json
import os
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_data(n_samples=5000):
    """Create synthetic property data for training"""
    np.random.seed(42)
    
    data = []
    for _ in range(n_samples):
        # Base property characteristics
        square_feet = np.random.normal(15000, 5000)
        square_feet = max(1000, square_feet)
        
        building_age = np.random.exponential(15)
        building_age = min(50, building_age)
        
        num_floors = np.random.poisson(8) + 1
        occupancy_rate = np.random.beta(9, 2)  # Higher occupancy rates
        
        # Location scores
        walk_score = np.random.normal(75, 15)
        walk_score = np.clip(walk_score, 0, 100)
        
        transit_score = np.random.normal(70, 20)
        transit_score = np.clip(transit_score, 0, 100)
        
        crime_rate = np.random.gamma(2, 25)
        crime_rate = np.clip(crime_rate, 0, 100)
        
        school_rating = np.random.normal(7, 1.5)
        school_rating = np.clip(school_rating, 1, 10)
        
        distance_to_downtown = np.random.exponential(5)
        distance_to_downtown = min(20, distance_to_downtown)
        
        # Financial characteristics
        revenue_per_sqft = np.random.normal(50, 15)
        revenue_per_sqft = max(20, revenue_per_sqft)
        annual_revenue = square_feet * revenue_per_sqft
        
        expense_ratio = np.random.normal(0.3, 0.1)
        expense_ratio = np.clip(expense_ratio, 0.1, 0.6)
        expenses = annual_revenue * expense_ratio
        
        cap_rate = np.random.normal(0.06, 0.02)
        cap_rate = np.clip(cap_rate, 0.03, 0.12)
        
        net_operating_income = annual_revenue - expenses
        
        # Calculate property value using income approach with adjustments
        base_value = net_operating_income / cap_rate
        
        # Adjustments for location and property characteristics
        location_multiplier = (walk_score/100 * 0.1 + transit_score/100 * 0.05 - 
                             crime_rate/100 * 0.08 + school_rating/10 * 0.03)
        
        age_adjustment = -building_age * 0.01  # Depreciation
        floor_bonus = min(num_floors * 0.02, 0.15)  # Height premium
        occupancy_adjustment = (occupancy_rate - 0.9) * 0.1  # Occupancy impact
        
        total_adjustment = 1 + location_multiplier + age_adjustment + floor_bonus + occupancy_adjustment
        property_value = base_value * total_adjustment
        
        # Add some noise
        property_value *= np.random.normal(1, 0.05)
        property_value = max(property_value, 100000)  # Minimum value
        
        data.append({
            'square_feet': square_feet,
            'building_age': building_age,
            'num_floors': num_floors,
            'occupancy_rate': occupancy_rate,
            'walk_score': walk_score,
            'transit_score': transit_score,
            'crime_rate': crime_rate,
            'school_rating': school_rating,
            'distance_to_downtown': distance_to_downtown,
            'annual_revenue': annual_revenue,
            'expenses': expenses,
            'cap_rate': cap_rate,
            'net_operating_income': net_operating_income,
            'property_value': property_value
        })
    
    return pd.DataFrame(data)

def train_neural_network():
    """Train neural network model"""
    print("Generating training data...")
    df = create_synthetic_data(5000)
    
    # Prepare features (same order as in metadata)
    feature_columns = [
        'square_feet', 'building_age', 'num_floors', 'occupancy_rate',
        'walk_score', 'transit_score', 'crime_rate', 'school_rating', 
        'distance_to_downtown', 'annual_revenue', 'expenses', 'cap_rate', 'net_operating_income'
    ]
    
    X = df[feature_columns].values
    y = df['property_value'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training neural network with {X_train.shape[0]} samples...")
    
    # Create neural network model
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=(len(feature_columns),)),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mean_squared_error',
        metrics=['mean_absolute_error']
    )
    
    # Train model
    history = model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_test_scaled, y_test),
        verbose=1,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=15, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(patience=10, factor=0.5)
        ]
    )
    
    # Evaluate
    y_pred = model.predict(X_test_scaled).flatten()
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    accuracy = 100 - mape
    
    print(f"Neural Network Metrics:")
    print(f"  MAE: ${mae:,.2f}")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  R²: {r2:.4f}")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  Accuracy: {accuracy:.2f}%")
    
    # Save model
    model.save('/app/models/neural_network_model.h5')
    print("Neural network model saved to /app/models/neural_network_model.h5")
    
    return model

if __name__ == "__main__":
    print("Training Neural Network for Property Valuation Ensemble...")
    train_neural_network()
    print("Training complete!")