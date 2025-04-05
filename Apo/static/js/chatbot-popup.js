class MentalHealthChatbotPopup {
    constructor(options = {}) {
        this.options = {
            apiUrl: options.apiUrl || 'http://localhost:5000/chatbot',
            buttonId: options.buttonId || 'open-chatbot-btn',
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Create the popup container
        this.createPopupContainer();
        
        // Add the open button if it doesn't exist
        if (!document.getElementById(this.options.buttonId)) {
            this.createOpenButton();
        }
        
        // Add event listeners
        this.setupEventListeners();
    }
    
    createPopupContainer() {
        const popup = document.createElement('div');
        popup.id = 'chatbot-popup';
        popup.className = 'chatbot-popup';
        popup.style.display = 'none';
        
        popup.innerHTML = `
            <div class="chatbot-popup-content">
                <div class="chatbot-popup-header">
                    <h2>Mental Health Support</h2>
                    <button class="close-chatbot">&times;</button>
                </div>
                <div class="chatbot-iframe-container">
                    <iframe src="${this.options.apiUrl}" 
                            frameborder="0" 
                            allow="camera; microphone">
                    </iframe>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);
    }
    
    createOpenButton() {
        const button = document.createElement('button');
        button.id = this.options.buttonId;
        button.className = 'open-chatbot-button';
        button.innerHTML = `
            <i class="fas fa-comments"></i>
            <span>Chat with Support</span>
        `;
        document.body.appendChild(button);
    }
    
    setupEventListeners() {
        // Open button click
        document.getElementById(this.options.buttonId).addEventListener('click', () => {
            this.openPopup();
        });
        
        // Close button click
        document.querySelector('.close-chatbot').addEventListener('click', () => {
            this.closePopup();
        });
        
        // Close when clicking outside
        document.getElementById('chatbot-popup').addEventListener('click', (e) => {
            if (e.target.id === 'chatbot-popup') {
                this.closePopup();
            }
        });
    }
    
    openPopup() {
        const popup = document.getElementById('chatbot-popup');
        popup.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    closePopup() {
        const popup = document.getElementById('chatbot-popup');
        popup.style.display = 'none';
        document.body.style.overflow = ''; // Restore scrolling
    }
}

// Make the chatbot popup globally accessible
window.MentalHealthChatbotPopup = MentalHealthChatbotPopup; 