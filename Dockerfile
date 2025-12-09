FROM python:3.11-slim

# Avoid Python writing .pyc files & enable unbuffered logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# System deps (optional, for things like geo libs / SSL / build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) Dev tools if you want the same image for CI & prod
# COPY requirements-dev.txt .
# RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the rest of the application code
COPY . .

EXPOSE 8501

# Default command: run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
