#!/usr/bin/env bash
set -euo pipefail

# Clean previous build artifacts
rm -rf package my_deployment_package.zip

# Create a fresh directory for the Lambda package
mkdir -p package

# Export requirements using uv and install them into the package directory
# This ensures we only get runtime dependencies and matches the lockfile exactly
uv export --format requirements-txt --no-dev --no-hashes > requirements.txt
pip install \
--platform manylinux2014_aarch64 \
--target=package \
--implementation cp \
--python-version 3.13 \
--only-binary=:all: --upgrade -r requirements.txt

rm requirements.txt

# Package the installed dependencies
cd package
zip -qr ../my_deployment_package.zip .
cd ..

# Add the Lambda entry point and source code
zip -q my_deployment_package.zip lambda_function.py
zip -qr my_deployment_package.zip ./src
