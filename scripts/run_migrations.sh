#!/bin/bash
set -e

# The only job of this script is to run the upgrade.
# The proxy is now handled by cloudbuild.yaml.
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."