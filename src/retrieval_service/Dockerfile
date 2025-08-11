# --- STAGE 1: The Builder ---
# This stage installs all the dependencies into a clean environment
FROM python:3.12-slim AS builder

# Set the working directory
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- STAGE 2: The Final Image ---
# This stage builds the final, lightweight container
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install runtime system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Set the port the container will listen on
ENV PORT 8080

# The command to run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 "retrieval_service:create_app()"