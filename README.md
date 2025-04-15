# Sign Language Recognition API

## Prerequisites

- Python 3.8 or higher
- eSpeak (Text-to-Speech engine)
  - Windows: Download and install from [eSpeak official website](http://espeak.sourceforge.net/download.html)
  - Linux: `sudo apt-get install espeak`
  - macOS: `brew install espeak`

## Setup

1. Clone the repository
2. Download the pre-trained model:
   - [Download asl_model.h5](https://drive.google.com/file/d/1gboxQCJ1FDzyzMWHkmjj6rid-BG88VtV/view?usp=sharing)
   - Place the downloaded model file in the project root directory
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make sure eSpeak is properly installed and accessible from your system's PATH

## Running the API

```bash
# Start the API server
python api.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check - GET `/`

Verifies the API is running and returns available endpoints.

**Response:**
```json
{
    "status": "success",
    "message": "Sign Language Recognition API is running",
    "endpoints": {
        "/predict": "POST - Send an image to get sign language prediction",
        "/predict_sequence": "POST - Send multiple images to get a sequence of predictions",
        "/predict_and_speak": "POST - Send multiple images to get a sequence of predictions and speech output"
    }
}
```

### 2. Single Prediction - POST `/predict`

Predicts a single sign language gesture from an image.

**Request Options:**

1. Form Data:
```http
POST /predict
Content-Type: multipart/form-data

image: <image_file>
```

2. JSON:
```http
POST /predict
Content-Type: application/json

{
    "image": "<base64_encoded_image>"
}
```

**Response:**
```json
{
    "status": "success",
    "prediction": "A",
    "confidence": 0.98,
    "all_predictions": {
        "A": 0.98,
        "B": 0.01,
        ...
    }
}
```

### 3. Sequence Prediction - POST `/predict_sequence`

Predicts multiple signs from a sequence of images and combines them into a sentence.

**Request Options:**

1. Form Data:
```http
POST /predict_sequence
Content-Type: multipart/form-data

image1: <image_file>
image2: <image_file>
...
```

2. JSON:
```http
POST /predict_sequence
Content-Type: application/json

{
    "images": [
        "<base64_encoded_image1>",
        "<base64_encoded_image2>",
        ...
    ]
}
```

**Response:**
```json
{
    "status": "success",
    "individual_predictions": [
        {
            "prediction": "H",
            "confidence": 0.95
        },
        {
            "prediction": "I",
            "confidence": 0.97
        }
    ],
    "sentence": "HI"
}
```

### 4. Predict and Speak - POST `/predict_and_speak`

Predicts multiple signs from images, combines them into a sentence, and generates speech audio.

**Request Options:**
Same as `/predict_sequence`

**Response:**
```json
{
    "status": "success",
    "individual_predictions": [
        {
            "prediction": "H",
            "confidence": 0.95
        },
        {
            "prediction": "I",
            "confidence": 0.97
        }
    ],
    "sentence": "HI",
    "audio_url": "/audio/<uuid>.wav"
}
```

### 5. Audio Retrieval - GET `/audio/<filename>`

Retrieve the generated audio file for text-to-speech output.

**Response:**
Audio file in WAV format
