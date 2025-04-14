FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libespeak-dev \
    espeak \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY asl__model.h5 .

RUN mkdir -p temp_audio

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.py

CMD ["python", "api.py"]