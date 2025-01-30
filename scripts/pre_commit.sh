#!/bin/bash

# Exit on error
set -e

echo "Running pre-commit hooks from project root..."
# Run pre-commit hooks using root poetry environment
poetry run pre-commit run --all-files

echo "Updating poetry.lock files for each service..."

# Array of service directories
services=("api" "worker" "db")

for service in "${services[@]}"; do
    echo "Updating poetry.lock for $service..."
    cd "src/$service"
    poetry lock --no-update
    cd ../..
done

echo "All checks completed successfully!"