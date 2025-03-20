# Dockerfile
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY app/ .

# Default command (can be changed via docker-compose)
CMD ["python", "main_terminal.py"]
