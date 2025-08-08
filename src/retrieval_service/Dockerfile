# Use an official Python base image hosted by Google
FROM gcr.io/distroless/python3-debian12

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Install production dependencies.
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . ./

# This is the correct production command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app.app:app"]