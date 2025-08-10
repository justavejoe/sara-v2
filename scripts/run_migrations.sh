#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# This script runs database migrations using Alembic.
# It uses the Cloud SQL Auth Proxy to securely connect to the database.

echo "--- Starting Cloud SQL Auth Proxy ---"
# Start the proxy in the background. The script will run from the project root.
./cloud-sql-proxy --project "$DB_PROJECT" --instance "$DB_INSTANCE" &

# Wait 5 seconds for the proxy to establish a connection
sleep 5

echo "--- Running Alembic migrations ---"
# Use the -c flag to explicitly tell Alembic where to find its config file.
# This is more robust than changing directories.
alembic -c src/retrieval_service/alembic.ini upgrade head

echo "--- Migrations completed successfully ---"