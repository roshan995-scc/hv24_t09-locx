import google.generativeai as genai
import os
import cv2
import numpy as np
import random
from fer import FER  # Import FER library for emotion detection
from dotenv import load_dotenv

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBnJ_vu93ErDrojrOk0M-wfQLQkTgc9oco"
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-pro"  # Using the correct model name

# Store conversation history
conversation_history = []

# Initialize FER emotion detector
detector = FER()

def detect_emotion(frame):
    """Detect emotion from a single frame."""
    try:
        # Create a copy of the frame for emotion detection
        detection_frame = frame.copy()
        
        # Ensure the frame is in BGR format (3 channels)
        if len(detection_frame.shape) == 2:
            detection_frame = cv2.cvtColor(detection_frame, cv2.COLOR_GRAY2BGR)
        
        # Resize frame if too large
        max_size = 640
        height, width = detection_frame.shape[:2]
        if width > max_size or height > max_size:
            scale = max_size / max(width, height)
            detection_frame = cv2.resize(detection_frame, (int(width * scale), int(height * scale)))
        
        print(f"Processing frame of shape: {detection_frame.shape}")
        print("Detecting emotions in frame...")
        
        # Detect emotions
        emotions = detector.detect_emotions(detection_frame)
        print(f"Raw emotions detected: {emotions}")

        if emotions and len(emotions) > 0 and emotions[0].get("emotions"):
            # Get all emotions and their probabilities
            emotion_probs = emotions[0]["emotions"]
            print(f"Emotion probabilities: {emotion_probs}")
            
            # Get the emotion with highest probability
            current_emotion = max(emotion_probs.items(), key=lambda x: x[1])[0]
            confidence = emotion_probs[current_emotion]
            print(f"Highest confidence emotion: {current_emotion} ({confidence:.2f})")
            
            # Lower the confidence threshold to 0.15 (15%) and add emotion-specific thresholds
            emotion_thresholds = {
                "happy": 0.15,
                "sad": 0.15,
                "angry": 0.15,
                "fear": 0.15,
                "disgust": 0.15,
                "surprise": 0.15,
                "neutral": 0.2  # Slightly higher threshold for neutral
            }
            
            threshold = emotion_thresholds.get(current_emotion, 0.15)
            if confidence > threshold:
                print(f"Emotion {current_emotion} detected with confidence {confidence:.2f} > threshold {threshold}")
                return current_emotion
            else:
                print(f"Confidence {confidence:.2f} below threshold {threshold} for {current_emotion}")
                
                # If confidence is too low, check if any other emotion has significant probability
                for emotion, prob in emotion_probs.items():
                    if emotion != current_emotion and prob > 0.15:
                        print(f"Found alternative emotion {emotion} with probability {prob:.2f}")
                        return emotion

        print("No emotions detected with sufficient confidence")
        return "neutral"
    except Exception as e:
        print(f"Error in emotion detection: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return "neutral"

def get_emotion_response(emotion):
    """Generate responses based on detected emotion."""
    responses = {
        "happy": [
            "I see that smile! What's making you so happy today?",
            "Your positive energy is contagious! Would you like to share what's bringing you joy?",
            "That's a beautiful smile! It's great to see you feeling happy. What's on your mind?"
        ],
        "sad": [
            "I notice you might be feeling down. Would you like to talk about what's bothering you?",
            "It's okay to feel sad sometimes. I'm here to listen if you want to share.",
            "I see you're feeling a bit low. Remember, it's okay to not be okay. Would you like to talk about it?"
        ],
        "angry": [
            "I sense some frustration. Would taking a few deep breaths help?",
            "It's okay to feel angry. Would you like to talk about what's upsetting you?",
            "I notice you're feeling upset. Sometimes talking about it can help. Would you like to share?"
        ],
        "fear": [
            "I see you might be feeling anxious. Remember, you're stronger than your fears.",
            "It's okay to feel afraid. Would you like to talk about what's concerning you?",
            "I notice you might be feeling anxious. Would you like to try some calming techniques?"
        ],
        "disgust": [
            "I see you're feeling displeased. Would you like to talk about what's bothering you?",
            "Your expression suggests something's troubling you. Would you like to share?",
            "I notice you seem uncomfortable. Is there something specific that's bothering you?"
        ],
        "surprise": [
            "You look surprised! Did something unexpected happen?",
            "That's quite a surprised expression! Would you like to share what caught you off guard?",
            "I see you're surprised! What's the story behind that expression?"
        ],
        "neutral": [
            "You seem calm and collected. How are you feeling today?",
            "I notice you're in a balanced state. Is there anything you'd like to talk about?",
            "You appear centered and focused. What's on your mind?"
        ]
    }

    return random.choice(responses.get(emotion, ["I'm here to chat if you'd like."]))

def generate_response(user_input):
    """Generate AI response based on user input."""
    try:
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(user_input)
            ai_response = response.text if hasattr(response, 'text') else "I'm having trouble generating a response right now."
        except Exception as e:
            print(f"\nAI API Error: {str(e)}")
            if "API key" in str(e):
                ai_response = "I'm having trouble connecting to my language model. Please check if your API key is set up correctly in the .env file."
            else:
                ai_response = "I'm having trouble connecting to my language model right now. But I can still chat based on what I observe!"
            
        # Add AI response to history
        conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response
    except Exception as e:
        return f"An error occurred: {str(e)}\nBut don't worry, I'm still here to chat!"

def generate_affirmation():
    """Generate a positive affirmation."""
    try:
        prompt = "Give me a positive affirmation to encourage someone feeling stressed or overwhelmed."
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else "Stay positive! You're doing great."
    except Exception as e:
        return "You are stronger than you know, and every day brings new opportunities for growth and joy."

def generate_meditation_guide():
    """Generate a short meditation guide."""
    try:
        prompt = "Provide a short 5-minute guided meditation script to help someone relax and reduce stress."
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else "Take a deep breath and relax."
    except Exception as e:
        return "Close your eyes, take three deep breaths, and focus on the present moment. You are safe and at peace." 