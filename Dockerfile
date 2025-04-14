FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libespeak-dev \
    espeak \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py .
COPY asl__model.h5 .

# Create directory for temporary audio files
RUN mkdir -p temp_audio

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.py

# Run the application
CMD ["python", "api.py"]