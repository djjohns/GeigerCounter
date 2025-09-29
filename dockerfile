# Use official Python base image
FROM python:3.14.0rc3-alpine3.22

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Chicago

# Set working directory
WORKDIR /app

# Copy code
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variable
ENV STREAMLIT_PORT=8501

# Expose Streamlit port
EXPOSE 8501

# Non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501","--server.address=0.0.0.0", "--server.enableCORS=false"]