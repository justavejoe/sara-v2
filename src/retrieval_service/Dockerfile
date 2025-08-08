# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12-slim 

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# --- Builder Stage ---
# This stage installs the dependencies
FROM base AS builder
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# This stage copies the installed dependencies and the application code
FROM base AS final
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

# Set the port the container will listen on
ENV PORT 8080

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app.app:app"]