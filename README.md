# Sign Language to Text and Speech Converter

## Overview
This application converts sign language gestures to text and speech using a deep learning model. It provides a Flask API that accepts images of sign language gestures and returns the corresponding text and audio output.

## Deployment Guide

### Prerequisites
1. A Render account
2. A cloud storage account (Google Drive, AWS S3, or similar) to host the model file
3. Docker installed locally for testing

### Model Hosting
1. Upload the `asl__model.h5` file to your preferred cloud storage service
2. Get a direct download URL for the model file
3. Make sure the URL is publicly accessible

### Deployment Steps

1. **Set up Environment Variables on Render**
   - Create a new Web Service on Render
   - Add the following environment variable:
     - `MODEL_URL`: Your cloud storage URL for the model file

2. **Deploy to Render**
   - Connect your GitHub repository to Render
   - Select the repository and branch
   - Choose "Docker" as the environment
   - Set the following:
     - Name: Your service name
     - Environment Variables: Add MODEL_URL
     - Instance Type: Choose appropriate instance (minimum 512MB)

3. **Verify Deployment**
   - Once deployed, test the API endpoints:
     - GET `/`: Check if the service is running
     - POST `/predict`: Test single image prediction
     - POST `/predict_sequence`: Test multiple image predictions
     - POST `/predict_and_speak`: Test prediction with speech output

## Local Development

1. Clone the repository
2. Create a `.env` file with your MODEL_URL
3. Run with Docker:
   ```bash
   docker-compose up --build
   ```

## API Endpoints

- `GET /`: Service health check
- `POST /predict`: Single image prediction
- `POST /predict_sequence`: Multiple image predictions
- `POST /predict_and_speak`: Predictions with speech output
- `GET /audio/<filename>`: Get generated audio file

## Notes
- The model file is ~250MB and is downloaded during container build
- Ensure your cloud storage URL is stable and publicly accessible
- The temp_audio directory is used for temporary storage of generated speech files
