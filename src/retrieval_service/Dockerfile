# --- STAGE 1: The Builder ---
# This stage installs all the dependencies into a clean environment
FROM python:3.12-slim AS builder

# Set the working directory
WORKDIR /app

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

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Set the port the container will listen on
ENV PORT 8080

# The command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app.app:app"]