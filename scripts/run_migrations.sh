#!/bin/bash
set -e

# This script runs database migrations using Alembic.
# It uses the Cloud SQL Auth Proxy to securely connect to the database.

echo "--- Starting Cloud SQL Auth Proxy ---"
# Start the proxy in the background using v2.x syntax
./cloud-sql-proxy "${DB_PROJECT}:${DB_REGION}:${DB_INSTANCE}" --address=0.0.0.0 --port=5432 &
PROXY_PID=$!

# Wait 5 seconds for the proxy to establish a connection
sleep 5

echo "--- Running Alembic migrations ---"
alembic -c src/retrieval_service/alembic.ini upgrade head

echo "--- Migrations completed successfully ---"

# Stop the proxy
kill $PROXY_PID
