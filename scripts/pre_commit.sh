#!/bin/bash

set -e

echo "Running pre-commit hooks from project root..."
poetry run pre-commit run --all-files

echo "Updating poetry.lock files for each service..."

services=("api" "worker" "db")

for service in "${services[@]}"; do
    echo "Updating poetry.lock for $service..."
    cd "src/$service"
    poetry lock --no-update
    cd ../..
done

echo "All checks completed successfully!"