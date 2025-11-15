FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
