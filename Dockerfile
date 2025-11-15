# Use official lightweight Python base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system-level dependencies required by OpenCV, Torch, Ultralytics
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgomp1 \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies (Torch, Ultralytics, Supabase, Flask, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Cloud Run expects gunicorn to bind to PORT env variable
ENV PORT=8080

# Expose the application port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
