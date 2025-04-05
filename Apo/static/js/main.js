// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const detectedEmotion = document.getElementById('detected-emotion');
const emotionOverlay = document.getElementById('emotion-overlay');
const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

let stream = null;
let isProcessing = false;
let lastEmotionCheck = 0;
const EMOTION_CHECK_INTERVAL = 3000; // Check emotion every 3 seconds
let emotionCheckInterval = null;

// Initialize webcam
async function initWebcam() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user',
                frameRate: { ideal: 30 }
            } 
        });
        video.srcObject = stream;
        await video.play();
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        console.log('Webcam initialized with dimensions:', canvas.width, 'x', canvas.height);
        
        // Start drawing video to canvas and emotion detection
        drawVideoToCanvas();
        startEmotionDetection();
    } catch (error) {
        console.error('Error accessing webcam:', error);
        // Don't show alert, just update the UI to indicate webcam is not available
        video.style.display = 'none';
        canvas.style.display = 'none';
        emotionOverlay.style.display = 'none';
        detectedEmotion.textContent = 'Camera not available';
    }
}

// Draw video to canvas
function drawVideoToCanvas() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        // Clear the canvas first
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Draw the video frame
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    }
    requestAnimationFrame(drawVideoToCanvas);
}

// Start emotion detection loop
function startEmotionDetection() {
    if (emotionCheckInterval) {
        clearInterval(emotionCheckInterval);
    }
    emotionCheckInterval = setInterval(checkEmotion, EMOTION_CHECK_INTERVAL);
}

// Check emotion from the current frame
async function checkEmotion() {
    if (isProcessing) return;
    
    try {
        const currentTime = Date.now();
        if (currentTime - lastEmotionCheck < EMOTION_CHECK_INTERVAL) return;
        
        isProcessing = true;
        
        // Ensure video is playing and has data
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
            console.log('Video not ready yet');
            return;
        }
        
        // Draw current frame to canvas with better quality
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Apply some basic image processing to improve detection
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixelData = imageData.data;
        
        // Increase contrast slightly
        for (let i = 0; i < pixelData.length; i += 4) {
            pixelData[i] = pixelData[i] * 1.1;     // Red
            pixelData[i + 1] = pixelData[i + 1] * 1.1; // Green
            pixelData[i + 2] = pixelData[i + 2] * 1.1; // Blue
        }
        
        ctx.putImageData(imageData, 0, 0);
        
        // Get image data with higher quality and better compression
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
        
        console.log('Sending frame for emotion detection...');
        const response = await fetch('/detect_emotion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageDataUrl })
        });
        
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('Received emotion:', responseData.emotion);
        
        // Get current emotion from the display
        const currentEmotion = detectedEmotion.textContent.toLowerCase();
        
        // Only update if we got a valid emotion and it's different from the current one
        if (responseData.emotion && responseData.emotion !== 'neutral' && 
            responseData.emotion !== currentEmotion) {
            
            console.log('Emotion changed from', currentEmotion, 'to', responseData.emotion);
            updateEmotion(responseData.emotion);
            
            // Get bot's response for the new emotion
            try {
                const botResponse = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: 'emotion_change',
                        emotion: responseData.emotion 
                    })
                });
                
                if (botResponse.ok) {
                    const botData = await botResponse.json();
                    console.log('Bot response:', botData.response);
                    addMessageToChat('bot', botData.response);
                } else {
                    console.error('Failed to get bot response:', botResponse.status);
                }
            } catch (error) {
                console.error('Error getting bot response:', error);
            }
        }
        
        lastEmotionCheck = currentTime;
    } catch (error) {
        console.error('Error checking emotion:', error);
    } finally {
        isProcessing = false;
    }
}

// Initialize the chat interface
async function initialize() {
    setupEventListeners();
    setupLoadingStates();
    // Initialize webcam in the background
    initWebcam().catch(console.error);
}

// Set up loading states
function setupLoadingStates() {
    sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    sendButton.disabled = false;
}

// Set up event listeners
function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// Show loading state
function showLoading() {
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    sendButton.disabled = true;
}

// Hide loading state
function hideLoading() {
    sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    sendButton.disabled = false;
}

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    if (message === '' || isProcessing) return;

    isProcessing = true;
    showLoading();

    // Add user message to chat
    addMessageToChat('user', message);
    userInput.value = '';

    // Send to backend and get response
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        // Update emotion display with animation
        updateEmotion(data.emotion);
        
        // Add bot response to chat
        addMessageToChat('bot', data.response);
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
    } finally {
        isProcessing = false;
        hideLoading();
    }
}

// Quick message function for affirmation and meditation buttons
function sendQuickMessage(type) {
    userInput.value = type;
    sendMessage();
}

// Add message to chat with animation
function addMessageToChat(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = `<p>${message}</p>`;
    
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

// Update emotion display with animation
function updateEmotion(emotion) {
    const emotionElement = document.getElementById('detected-emotion');
    const overlayElement = document.getElementById('emotion-overlay');
    
    // Add fade out effect
    emotionElement.style.opacity = '0';
    overlayElement.style.opacity = '0';
    
    setTimeout(() => {
        emotionElement.textContent = emotion;
        overlayElement.textContent = `Detected: ${emotion}`;
        
        // Add fade in effect
        emotionElement.style.opacity = '1';
        overlayElement.style.opacity = '1';
    }, 200);
}

// Clean up when page is unloaded
window.addEventListener('beforeunload', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});

// Start the application
initialize(); 