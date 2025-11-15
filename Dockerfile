# Dockerfile (replace existing)
FROM python:3.11-slim

WORKDIR /app

# Install system libs required by OpenCV, torch CPU, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgl1-mesa-glx \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (we will install torch cpu separately for reliability)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU-only torch + torchvision wheels (stable) to avoid illegal-instruction
RUN pip install --no-cache-dir torch==2.1.0+cpu torchvision==0.16.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Then install remaining Python deps from requirements.txt (excluding torch/torchvision)
RUN sed -E 's/^torch.*$//I; s/^torchvision.*$//I' requirements.txt > /tmp/reqs-no-torch.txt && \
    pip install --no-cache-dir -r /tmp/reqs-no-torch.txt && rm -f /tmp/reqs-no-torch.txt

# Copy app
COPY . .

ENV PORT=8080
EXPOSE 8080

# Run gunicorn
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
