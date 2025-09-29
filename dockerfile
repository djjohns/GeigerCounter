# Use official Python base image
FROM python:3.14.0rc3-alpine3.22

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

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]