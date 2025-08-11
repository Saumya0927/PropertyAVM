#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec avm-postgres pg_isready -U avm_user; do
  echo "PostgreSQL is not ready yet..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Initialize database schema
echo "Initializing database schema..."
docker exec -i avm-postgres psql -U avm_user -d property_valuation < infrastructure/init.sql

echo "Database schema initialized!"

# Generate and load synthetic data
echo "Generating synthetic data..."
cd data-generator
python3 generate_synthetic_data.py

echo "Loading synthetic data into database..."
python3 load_data.py

echo "Database initialization complete!"