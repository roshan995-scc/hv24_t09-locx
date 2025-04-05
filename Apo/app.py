from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for
from mentalhealth import detect_emotion, generate_response, generate_affirmation, generate_meditation_guide
import base64
import cv2
import numpy as np

# Create a Blueprint for the chatbot
chatbot_bp = Blueprint('chatbot', __name__, 
                      template_folder='templates',
                      static_folder='static')

@chatbot_bp.route('/')
def chatbot_home():
    return render_template('index.html')

@chatbot_bp.route('/detect_emotion', methods=['POST'])
def detect_emotion_endpoint():
    try:
        # Get the base64 image data from the request
        image_data = request.json.get('image')
        if not image_data:
            print("No image data received")
            return jsonify({'emotion': 'neutral'})
            
        # Remove the data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("Failed to decode image")
            return jsonify({'emotion': 'neutral'})
            
        print(f"Processing frame of shape: {frame.shape}")
        
        # Detect emotion using the frame
        emotion = detect_emotion(frame)
        print(f"Detected emotion: {emotion}")
        
        return jsonify({'emotion': emotion})
    except Exception as e:
        print(f"Error in emotion detection: {str(e)}")
        return jsonify({'emotion': 'neutral'})

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    emotion = data.get('emotion', 'neutral')
    
    try:
        if message == 'affirmation':
            response = generate_affirmation()
        elif message == 'meditation':
            response = generate_meditation_guide()
        elif message == 'emotion_change':
            response = get_emotion_response(emotion)
        else:
            response = generate_response(message)
            
        return jsonify({
            'response': response,
            'emotion': emotion
        })
    except Exception as e:
        return jsonify({
            'response': f"An error occurred: {str(e)}",
            'emotion': 'neutral'
        }), 500

# Create the main Flask app
app = Flask(__name__)

# Add a root route that redirects to the chatbot
@app.route('/')
def root():
    return redirect(url_for('chatbot.chatbot_home'))

# Register the chatbot blueprint with a URL prefix
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 