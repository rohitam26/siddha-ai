# Multi-stage Dockerfile for Siddha AI (Backend & Static Frontend)

FROM python:3.12-slim AS backend

WORKDIR /app

# Install system dependencies for OpenCV headless and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ML artifacts, backend, and data
COPY ml/ ./ml/
COPY backend/ ./backend/
COPY data/ ./data/

ENV PYTHONPATH=/app/backend
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "backend/main.py"]
