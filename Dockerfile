FROM python:3.11-slim

# Set working directory
WORKDIR /app

# =============================
# Install system dependencies
# =============================
# libgl1 -> fixes OpenCV: "libGL.so.1 not found"
# libglib2.0-0 -> needed by cv2
# libsm6, libxext6, libxrender1 -> needed for image processing
# git -> needed in case ultralytics pulls extra deps
# =============================
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better build caching)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy entire backend code into container
COPY . .

# Cloud Run requires PORT env
ENV PORT=8080

EXPOSE 8080

# =============================
# Gunicorn command for Cloud Run
# Cloud Run uses only 1 worker recommended
# =============================
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
