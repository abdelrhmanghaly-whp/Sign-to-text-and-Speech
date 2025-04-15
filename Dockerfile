FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies for OpenCV and pyttsx3
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libespeak-ng1 \
    espeak-ng-data \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model (Git LFS will handle the large file)
COPY . .

# Create directory for temporary audio files
RUN mkdir -p temp_audio && chmod 777 temp_audio

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Checking for model file..."\n\
if [ ! -f "/app/asl__model.h5" ]; then\n\
  echo "Model file not found!"\n\
  ls -la /app\n\
  exit 1\n\
fi\n\
echo "Model file exists. Starting server..."\n\
exec gunicorn --workers=1 --timeout=180 --bind 0.0.0.0:${PORT:-5000} api:app\n\
' > /app/startup.sh && chmod +x /app/startup.sh

# Expose the port the app runs on
EXPOSE ${PORT:-5000}

# Use our startup script to serve the application
CMD ["/app/startup.sh"]