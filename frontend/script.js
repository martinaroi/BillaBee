document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search');
    
    const welcomeSection = document.getElementById('welcome-section');
    const chatContainer = document.getElementById('chat-container');
    const transitionEffect = document.getElementById('transition-effect');
    
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    
    /**
     * Creates and adds a message bubble to the chat box.
     * @param {string} text - The message content.
     * @param {string} sender - 'user' or 'bot'.
     */

    // Function to add a message to the chat box
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add("message");

        if (sender === 'user') {
            messageDiv.classList.add("user-message");
        } else {
            messageDiv.classList.add("bot-message");
        }
        
        // Create a separate element for the text content
        const textElement = document.createElement('p');
        textElement.textContent = text;
        
        // Create a separate element for the timestamp
        const timeElement = document.createElement('span');
        timeElement.classList.add('timestamp'); // Give it a class for potential styling
        timeElement.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Add the text and timestamp to the message bubble
        messageDiv.appendChild(textElement);
        messageDiv.appendChild(timeElement);
        
        // Add the completed bubble to the chat box
        chatBox.appendChild(messageDiv);    

        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    /**
     * Shows the "Billa is typing..." indicator.
     */
    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = "typing-indicator";
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span>Billa the Bee is typing...</span>
        `; 
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    /**
     * Removes the typing indicator.
     */
    function removeTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Handles what happens when the user sends a message from within the chat.
     */
    function handleChatSendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            chatInput.value = '';
            showTyping();

            setTimeout(() => {
                removeTyping();
                const botResponse = "That's a great point! Let's keep this buzz going. 🐝";
                addMessage(botResponse, 'bot');
            }, 1000);
        }
    }

    // --- Event Listeners ---

    // STARTING the chat from the welcome screen.
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Stop page reload

        const initialQuery = searchInput.value.trim();

        // CORRECTED: This now checks if the user typed something.
        if (initialQuery !== "") {
            welcomeSection.style.display = 'none';
            chatContainer.style.display = "flex";
            
            addMessage(initialQuery, 'user');
            showTyping();

            setTimeout(() => {
                removeTyping();
                const botResponse = "Welcome to BillaBee! How can I assist you today?";
                addMessage(botResponse, 'bot');
            }, 1000);
        }
    });

    // Event listener for the "Buzz!" button inside the chat
    chatSend.addEventListener('click', handleChatSendMessage);

    // Event listener for pressing "Enter" inside the chat
    chatInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            handleChatSendMessage();
        }
    });
});