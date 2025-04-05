class MentalHealthChatbot {
    constructor(options = {}) {
        this.options = {
            apiUrl: options.apiUrl || 'http://localhost:5000/chatbot',
            containerId: options.containerId || 'chatbot-container',
            position: options.position || 'bottom-right',
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Create container if it doesn't exist
        if (!document.getElementById(this.options.containerId)) {
            const container = document.createElement('div');
            container.id = this.options.containerId;
            container.className = `chatbot-container ${this.options.position}`;
            document.body.appendChild(container);
        }
        
        // Load the chatbot UI
        this.loadChatbotUI();
    }
    
    loadChatbotUI() {
        const container = document.getElementById(this.options.containerId);
        
        // Create the chatbot HTML structure
        container.innerHTML = `
            <div class="chatbot-wrapper">
                <div class="chatbot-header">
                    <div class="header-content">
                        <i class="fas fa-brain"></i>
                        <h1>Mental Health Support</h1>
                    </div>
                    <div class="emotion-display">
                        <span class="emotion-label">Current Emotion:</span>
                        <span id="detected-emotion">Neutral</span>
                    </div>
                </div>

                <div class="video-container">
                    <video id="webcam" autoplay playsinline></video>
                    <canvas id="canvas"></canvas>
                    <div class="emotion-overlay" id="emotion-overlay"></div>
                </div>

                <div class="chat-messages" id="chat-messages">
                    <div class="message bot-message">
                        <div class="message-content">
                            <p>Welcome! I'm here to support you. You can:</p>
                            <ul>
                                <li>Chat with me about anything</li>
                                <li>Click the Affirmation button for a positive message</li>
                                <li>Click the Meditation button for a relaxation guide</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="chat-input-container">
                    <div class="input-wrapper">
                        <input type="text" id="user-input" placeholder="Type your message here...">
                        <button id="send-button">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="quick-actions">
                        <button class="action-button" onclick="window.chatbot.sendQuickMessage('affirmation')">
                            <i class="fas fa-star"></i> Affirmation
                        </button>
                        <button class="action-button" onclick="window.chatbot.sendQuickMessage('meditation')">
                            <i class="fas fa-peace"></i> Meditation
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Load the chatbot functionality
        this.initializeChatbot();
    }
    
    initializeChatbot() {
        // Initialize webcam and emotion detection
        this.initWebcam();
        this.setupEventListeners();
    }
    
    // Add all the existing chatbot functionality here...
    // (Copy the relevant functions from main.js)
    
    sendQuickMessage(type) {
        const userInput = document.getElementById('user-input');
        userInput.value = type;
        this.sendMessage();
    }
}

// Make the chatbot globally accessible
window.MentalHealthChatbot = MentalHealthChatbot; 