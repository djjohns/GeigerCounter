# Dockerfile
FROM python:3.13-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Chicago \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Python deps (requires requirements.txt to exist)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && python -m pip install -r /app/requirements.txt

# App code
COPY . .

# Non-root user
RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
