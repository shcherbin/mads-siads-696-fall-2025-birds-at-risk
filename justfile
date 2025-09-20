set dotenv-required
set dotenv-load

# Install Python prod and dev dependencies.
install-python-dependencies:
	uv sync --frozen

# Run Python tests
test:
	pytest --cov=./src --cov-report=term-missing --ruff --ruff-format ./tests

# Download the source datasets from an S3 bucket
dowload-source-data:
	aws s3 sync s3://$AWS_S3_BUCKET/ notebooks/data