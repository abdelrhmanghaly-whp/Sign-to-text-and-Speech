import os
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import pyttsx3
import tempfile
import uuid
import os.path

# Configure TensorFlow to use CPU only
tf.config.set_visible_devices([], 'GPU')

print("Loading model...")
tf.keras.backend.clear_session()

model = tf.keras.models.load_model("asl__model.h5", compile=False)
print("Model loaded successfully")

print("Model ready for predictions")

labels_map = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
              'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

app = Flask(__name__)
CORS(app)


engine = pyttsx3.init()


temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_audio')
os.makedirs(temp_dir, exist_ok=True)

def process_image(img):
    img = cv2.resize(img, (150, 150))
    img = np.array(img) / 255.0
    img = img.reshape(1, 150, 150, 3)
    
    prediction = model.predict(img)
    pred_index = np.argmax(prediction)
    pred_letter = labels_map[pred_index]
    confidence = float(prediction[0][pred_index])
    
    return {
        "prediction": pred_letter,
        "confidence": confidence
    }

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Sign Language Recognition API is running",
        "endpoints": {
            "/predict": "POST - Send an image to get sign language prediction",
            "/predict_sequence": "POST - Send multiple images to get a sequence of predictions",
            "/predict_and_speak": "POST - Send multiple images to get a sequence of predictions and speech output"
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type', '')
    
    if 'multipart/form-data' in content_type:
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {list(request.form.keys())}")
        
        if not request.files:
            return jsonify({"error": "No files found in the request"}), 400
        
        image_file = None
        for key, file in request.files.items():
            if file.content_type and file.content_type.startswith('image/'):
                image_file = file
                break
        
        if not image_file and request.files:
            image_file = list(request.files.values())[0]
        
        if not image_file:
            return jsonify({"error": "No image file found in the request"}), 400
        
        try:
            img_array = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                return jsonify({"error": "Could not decode image data"}), 400
        except Exception as e:
            return jsonify({"error": f"Error processing form data: {str(e)}"}), 400
    
    elif 'application/json' in content_type:
        print(f"Request JSON keys: {list(request.json.keys()) if request.is_json else 'Not JSON'}")
        
        if not request.is_json:
            return jsonify({"error": "Invalid JSON format in request"}), 400
            
        if 'image' not in request.json:
            return jsonify({"error": "No 'image' key found in JSON data"}), 400
        
        try:
            encoded_img = request.json['image']
            print(f"Image data type: {type(encoded_img)}")
            print(f"Image data starts with: {encoded_img[:50]}...")
            
            if encoded_img.startswith('data:image'):
                encoded_img = encoded_img.split(',')[1]
                print("Removed data URL prefix")
                
            img_bytes = base64.b64decode(encoded_img)
            img_array = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({"error": "Could not decode image data from base64 string"}), 400
                
        except Exception as e:
            print(f"JSON processing error: {str(e)}")
            return jsonify({"error": f"Error processing JSON data: {str(e)}"}), 400
    
    else:
        return jsonify({"error": f"Unsupported Content-Type: {content_type}. Use 'multipart/form-data' for form data or 'application/json' for JSON data"}), 400
    
    try:
        img = cv2.resize(img, (150, 150))
        img = np.array(img) / 255.0
        img = img.reshape(1, 150, 150, 3)
        
        prediction = model.predict(img)
        pred_index = np.argmax(prediction)
        pred_letter = labels_map[pred_index]
        confidence = float(prediction[0][pred_index])
        
        return jsonify({
            "status": "success",
            "prediction": pred_letter,
            "confidence": confidence,
            "all_predictions": {
                label: float(prediction[0][i]) 
                for i, label in enumerate(labels_map)
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_sequence', methods=['POST'])
def predict_sequence():
    try:
        results = []
        
        if request.is_json and 'images' in request.json:
            encoded_images = request.json['images']
            
            for encoded_img in encoded_images:
                if encoded_img.startswith('data:image'):
                    encoded_img = encoded_img.split(',')[1]
                
                img_bytes = base64.b64decode(encoded_img)
                img_array = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                results.append(process_image(img))
        
        elif request.files:
            image_files = [file for key, file in request.files.items() if key.startswith('image')]
            
            if not image_files:
                return jsonify({"error": "No images provided in form data"}), 400
                
            for file in image_files:
                img_array = np.frombuffer(file.read(), np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                results.append(process_image(img))
        
        else:
            return jsonify({"error": "No images provided. Send either JSON with 'images' array or form-data with multiple 'image' files"}), 400
        
        sentence = ""
        prev_letter = ""
        
        for result in results:
            pred_letter = result["prediction"]
            confidence = result["confidence"]
            
            if confidence > 0.8 and pred_letter != "nothing":
                if pred_letter == "space":
                    if not sentence.endswith(" "):
                        sentence += " "
                elif pred_letter == "del":
                    if sentence:
                        sentence = sentence[:-1]
                else:
                    sentence += pred_letter
                prev_letter = pred_letter
        
        return jsonify({
            "status": "success",
            "individual_predictions": results,
            "sentence": sentence
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_and_speak', methods=['POST'])
def predict_and_speak():
    try:
        results = []
        
        if request.is_json and 'images' in request.json:
            encoded_images = request.json['images']
            
            for encoded_img in encoded_images:
                if encoded_img.startswith('data:image'):
                    encoded_img = encoded_img.split(',')[1]
                
                img_bytes = base64.b64decode(encoded_img)
                img_array = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                results.append(process_image(img))
        
        elif request.files:
            image_files = [file for key, file in request.files.items() if key.startswith('image')]
            
            if not image_files:
                return jsonify({"error": "No images provided in form data"}), 400
                
            for file in image_files:
                img_array = np.frombuffer(file.read(), np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                results.append(process_image(img))
        
        else:
            return jsonify({"error": "No images provided. Send either JSON with 'images' array or form-data with multiple 'image' files"}), 400
        
        sentence = ""
        prev_letter = ""
        
        for result in results:
            pred_letter = result["prediction"]
            confidence = result["confidence"]
            
            if confidence > 0.8 and pred_letter != "nothing":
                if pred_letter == "space":
                    if not sentence.endswith(" "):
                        sentence += " "
                elif pred_letter == "del":
                    if sentence:
                        sentence = sentence[:-1]
                else:
                    sentence += pred_letter
                prev_letter = pred_letter
        
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(temp_dir, audio_filename)
        
        engine.save_to_file(sentence, audio_path)
        engine.runAndWait()
        
        return jsonify({
            "status": "success",
            "individual_predictions": results,
            "sentence": sentence,
            "audio_url": f"/audio/{audio_filename}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>', methods=['GET'])
def get_audio(filename):
    try:
        audio_path = os.path.join(temp_dir, filename)
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        
        return send_file(audio_path, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)