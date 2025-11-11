#!/bin/bash

set -e
ENV_NAME="data_catalog_env"

echo "Creating Python virtual environment: $ENV_NAME"
python -m venv "$ENV_NAME"

if [ -f "$ENV_NAME/bin/activate" ]; then
    echo "Activating environment..."
    . "$ENV_NAME/bin/activate"
else
    echo "Could not find activate script in $ENV_NAME/bin/activate"
    exit 1
fi
