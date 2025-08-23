document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search');
    
    const welcomeSection = document.getElementById('welcome-section');
    const chatContainer = document.getElementById('chat-container');
    const transitionEffect = document.getElementById('transition-effect');
    
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const confirmButton = document.getElementById('confirm-button');
    
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
    async function handleChatSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return; 

        addMessage(message, 'user');
        chatInput.value = '';
        showTyping();

        const response = await fetch('http://127.0.0.1:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

            const data = await response.json();

            setTimeout(() => {
                removeTyping();
                addMessage(data.response, 'bot');
            }, 1000);
        }


    // --- Event Listeners ---

    // STARTING the chat from the welcome screen.
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); 

        const initialQuery = searchInput.value.trim();

        // CORRECTED: This now checks if the user typed something.
        if (initialQuery !== "") {
            welcomeSection.style.display = 'none';
            chatContainer.style.display = "flex";
            
            addMessage(initialQuery, 'user');
            showTyping();

            async function fetchInitialResponse() {
                const response = await fetch('http://127.0.0.1:5000/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: initialQuery })     
                });
                
                const data = await response.json();
                console.log("Received from API:", data);
                removeTyping();

                addMessage(data.response || "Here is your schedule:", 'bot');

                if (data.events && data.events.length > 0) {
                    showEventList(data.events);
                } else {
                    console.log("No events received to display.");
                }
            }
            fetchInitialResponse();
        }
    });

    function showEventList(events) {
        console.log("showEventList called with events:", events);
        const eventsContainer = document.getElementById('events-container');
        eventsContainer.innerHTML = ''; // Clear previous events
        

        events.forEach((event, index) => {
            const eventDiv = document.createElement('div');
            eventDiv.classList.add('event-card');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `event-${index}`;
            checkbox.value = index; 
            checkbox.checked = true;

            const label = document.createElement('label');
            label.htmlFor = `event-${index}`;
            label.innerText = `Event: ${event.summary} at ${event.start} - ${event.end}`;

            eventDiv.appendChild(checkbox);
            eventDiv.appendChild(label);
            eventsContainer.appendChild(eventDiv);
        });

        // Add button to confirm selected events
        const confirmButton = document.createElement('button');
        confirmButton.innerText = 'Confirm Events';
        confirmButton.id = 'confirm-button';
        confirmButton.classList.add('confirm-button');
        confirmButton.addEventListener('click', () => sendApprovedEvents(events));
        eventsContainer.appendChild(confirmButton);
    }

    function sendApprovedEvents(events) {
        const selectedEvents = [];
        events.forEach((event, index) => {
            const checkbox = document.getElementById(`event-${index}`);
            if (checkbox.checked) {
                selectedEvents.push(event);
            }
        });
        if (selectedEvents.length === 0) {
            alert("Select at least one event to proceed.");
            return;
        }

        // Proceed with sending the selected events
        fetch('http://127.0.0.1:5000/api/create_event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ events: selectedEvents })
        })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            alert("Events sent to Google Calendar!")
        });
    }

    // Event listener for the "Buzz!" button inside the chats
    chatSend.addEventListener('click', handleChatSendMessage);

    // Event listener for pressing "Enter" inside the chat
    chatInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            handleChatSendMessage();
        }
    });

});