# Stage 1: Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install dependencies for downloading model
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for model
RUN mkdir -p /app/model

# Set environment variables for model download
ARG MODEL_URL
ENV MODEL_URL=${MODEL_URL}

# Download model using direct download
RUN if [ ! -f /app/asl__model.h5 ]; then \
    echo "Downloading model..." && \
    wget -O /app/asl__model.h5 "https://drive.google.com/uc?export=download&id=${MODEL_URL}" || \
    (echo "Model download failed" && exit 1); \
    fi

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