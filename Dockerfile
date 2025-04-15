FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libespeak-ng1 \
    espeak-ng-data \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp_audio && chmod 777 temp_audio

# Expose the port the app runs on
EXPOSE 5000

# Use Gunicorn to serve the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]