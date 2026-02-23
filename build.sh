#!/usr/bin/env bash
set -euo pipefail

# Clean previous build artifacts
rm -rf package my_deployment_package.zip

# Create a fresh directory for the Lambda package
mkdir -p package

# Install only runtime dependencies defined in pyproject.toml (no dev group)
# The dot tells pip to read pyproject.toml in the current directory
pip install --target ./package .

# Package the installed dependencies
cd package
zip -r ../my_deployment_package.zip .
cd ..

# Add the Lambda entry point and source code
zip my_deployment_package.zip lambda_function.py
zip -r my_deployment_package.zip ./src
