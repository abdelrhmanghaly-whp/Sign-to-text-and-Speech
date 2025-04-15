# Stage 1: Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install dependencies for downloading model
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gdown

# Copy application code
COPY . .

# Create directory for model and download it
RUN mkdir -p /app/model

# Download model during build using gdown for Google Drive
ARG MODEL_URL
RUN gdown ${MODEL_URL} -O /app/asl__model.h5

# Stage 2: Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app .

# Create temp_audio directory
RUN mkdir -p /app/temp_audio

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]