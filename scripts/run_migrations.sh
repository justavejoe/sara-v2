#!/bin/bash
set -e

# This script runs database migrations using Alembic.
# It uses the Cloud SQL Auth Proxy to securely connect to the database.

echo "Starting Cloud SQL Auth Proxy..."
./cloud-sql-proxy --project "$_PROJECT" --instance "$_INSTANCE" &

# Wait for the proxy to be ready
sleep 5

echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed."