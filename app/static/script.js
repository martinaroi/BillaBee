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
    const eventsContainer = document.getElementById('events-container');
    
    /**
     * Creates and adds a message bubble to the chat box.
     * @param {string} text - The message content.
     * @param {string} sender - 'user' or 'bot'.
     */

    // --- Global state variable to hold the events from the AI ---
    let currentEvents = [];   

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
    async function handleUserQuery(message) {
        addMessage(message, 'user');
        showTyping();
        eventsContainer.innerHTML = ''; // Clear old events

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            console.log("Received from API:", data);

            removeTyping();
            addMessage(data.response || "Here is your schedule:", 'bot');

            if (data.events && data.events.length > 0) {
                // Store the events globally and display them
                currentEvents = data.events;
                showEventList();
            } else {
                currentEvents = []; // Clear the events if none are returned
            }
        } catch (error) {
            removeTyping();
            addMessage("Oh honey, something went wrong. Please try again.", 'bot');
            console.error("Error fetching from /api/chat:", error);
        }
    }

    function showEventList() {
        // This function now reads from the global 'currentEvents' variable
        eventsContainer.innerHTML = ''; // Clear previous events

        currentEvents.forEach((event, index) => {
            const eventDiv = document.createElement('div');
            eventDiv.classList.add('event-card');
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `event-${index}`;
            checkbox.checked = true; // Default to checked

            const label = document.createElement('label');
            label.htmlFor = `event-${index}`;
            // Correctly display the dateTime
            label.innerText = `Event: ${event.summary} at ${event.start.dateTime}`;

            eventDiv.appendChild(checkbox);
            eventDiv.appendChild(label);
            eventsContainer.appendChild(eventDiv);
        });

        // Add a single confirm button at the end
        if (currentEvents.length > 0) {
            const confirmButton = document.createElement('button');
            confirmButton.innerText = 'Confirm Events';
            confirmButton.id = 'confirm-button';
            confirmButton.addEventListener('click', sendApprovedEvents);
            eventsContainer.appendChild(confirmButton);
        }
    }

    async function sendApprovedEvents() {
        // This function also reads from the global 'currentEvents' variable
        const selectedEvents = [];
        currentEvents.forEach((event, index) => {
            const checkbox = document.getElementById(`event-${index}`);
            if (checkbox && checkbox.checked) {
                selectedEvents.push(event);
            }
        });

        if (selectedEvents.length === 0) {
            alert("Please select at least one event to confirm.");
            return;
        }

        const confirmButton = document.getElementById('confirm-button');
        if (confirmButton) {
            confirmButton.disabled = true;
            confirmButton.innerText = 'Creating...';
        }

        const requests = selectedEvents.map(event => {
            console.log("SENDING THIS JSON TO BACKEND:", event); // Final check of the data
            return fetch('http://127.0.0.1:5000/api/create_event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            });
        });

        try {
            const responses = await Promise.all(requests);
            const failed = responses.filter(res => !res.ok);
            if (failed.length > 0) {
                alert("Oops! Some events could not be created.");
            } else {
                alert("Success! All events added to your Google Calendar!");
            }
        } catch (error) {
            alert("A network error occurred.");
        } finally {
            eventsContainer.innerHTML = ''; // Clear events after attempting to create them
        }
    }

    // --- Event Listeners ---

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const initialQuery = searchInput.value.trim();
        if (initialQuery) {
            welcomeSection.style.display = 'none';
            chatContainer.style.display = "flex";
            handleUserQuery(initialQuery);
        }
    });

    chatSend.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            handleUserQuery(message);
            chatInput.value = '';
        }
    });

    chatInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            const message = chatInput.value.trim();
            if (message) {
                handleUserQuery(message);
                chatInput.value = '';
            }
        }
    });
});