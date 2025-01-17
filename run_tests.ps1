Write-Host "Running API tests..."
Push-Location src/api
poetry install
poetry run pytest
Pop-Location

Write-Host "Running Worker tests..."
Push-Location src/worker
poetry install
poetry run pytest
Pop-Location 