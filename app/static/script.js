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
    const beeIcons = document.querySelectorAll('.bee-icon');

    const userSelect = document.getElementById('user');
    const selectedUser = userSelect.value;
    /**
     * Creates and adds a message bubble to the chat box.
     * @param {string} text - The message content.
     * @param {string} sender - 'user' or 'bot'.
     */

    // --- Global state variable to hold the events from the AI ---
    let currentEvents = [];   

    // Function to switch user
    async function switchUser() {
        console.log("Switching to user:", selectedUser);

        try {
            const response = await fetch ('/api/set_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: selectedUser })
            });

            if(response.ok) {
                alert(`Switched to user: ${selectedUser}`);
            } else { 
                alert("Failed to switch user.");
            }
        } catch (error) {
            console.error("Error switching user:", error);
        }
    }

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
        const textElement = document.createElement('div');
        // For bot messages, allow Markdown -> sanitized HTML; user stays plain text
        if (sender === 'bot') {
            try {
                const html = marked.parse(text || '');
                textElement.innerHTML = DOMPurify.sanitize(html, {USE_PROFILES: {html: true}});
            } catch (e) {
                // Fallback to text if something goes wrong
                textElement.textContent = text;
            }
        } else {
            textElement.textContent = text;
        }
        
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

            if(data && data.status === 'success'){
                const tool_name = data.tool_name;
                const responseData = data.data;
            

                if(tool_name === 'reply_text'){
                    addMessage(responseData.text, 'bot');
                } else if (tool_name === 'find_event') {
                    currentEvents = responseData;
                    showEventList();
                } else if (tool_name === 'create_event') {
                    addMessage(responseData.message, 'bot');
                } else if (tool_name === 'delete_event' || tool_name === 'update_event') {
                    addMessage(responseData.message, 'bot');
                }

            } else {
                const errorMessage = data ? data.message : "An unknown error occurred.";
                addMessage(`Oops, something went wrong: ${errorMessage}`, 'bot');
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

            // Theme selector
            const themeSelect = document.createElement('select');
            themeSelect.id = `theme-${index}`;
            const themes = ['Auto','Work','Study','Exercise','Health','Wellbeing','Family','Social','Errand','Focus'];
            themes.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                themeSelect.appendChild(opt);
            });

            eventDiv.appendChild(checkbox);
            eventDiv.appendChild(label);
            eventDiv.appendChild(themeSelect);
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
                // Clone event to avoid mutating the original
                const eventCopy = JSON.parse(JSON.stringify(event));
                const themeSel = document.getElementById(`theme-${index}`);
                if (themeSel) {
                    const chosen = themeSel.value;
                    if (chosen && chosen !== 'Auto') {
                        eventCopy.theme = chosen;
                    }
                }
                selectedEvents.push(eventCopy);
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
            const messageforAI = `Please use the create_event tool to create an event with these exact details: ${JSON.stringify(event)}`;
            
            const requestBody = {
                message: messageforAI
            };

            return fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
        });

        try{
            const responses = await Promise.all(requests);

            const successful = responses.filter(res => res.ok);

            if (successful.length === selectedEvents.length) {
                alert("Success! All events added to your Google Calendar!");
            } else {
                alert(`Oops! ${successful.length} out of ${selectedEvents.length} events could not be created.`);
            }
        } catch (error) {
            alert("A network error occurred.");
        } finally {
            eventsContainer.innerHTML = ''; // Clear events after attempting to create them
            if (confirmButton) {
                confirmButton.disabled = false;
                confirmButton.innerText = 'Confirm Events';
            }
        }
    }

    // --- Event Listeners ---

    // Make the bee icons navigate back to the welcome screen
    beeIcons.forEach((icon) => {
        icon.setAttribute('title', 'Go to Home');
        icon.addEventListener('click', () => {
            // Show welcome, hide chat
            if (welcomeSection) welcomeSection.style.display = 'flex';
            if (chatContainer) chatContainer.style.display = 'none';
            // Optional: clear events panel and focus search
            if (eventsContainer) eventsContainer.innerHTML = '';
            if (searchInput) searchInput.focus();
        });
    });

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const initialQuery = searchInput.value.trim();
        if (initialQuery) {
            welcomeSection.style.display = 'none';
            chatContainer.style.display = "flex";
            handleUserQuery(initialQuery);
        }
    });

    // In a textarea, Enter should submit (unless Shift+Enter)
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            searchForm.requestSubmit();
        }
    });

    chatSend.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            handleUserQuery(message);
            chatInput.value = '';
        }
    });

    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const message = chatInput.value.trim();
            if (message) {
                handleUserQuery(message);
                chatInput.value = '';
            }
        }
    });


    searchInput.addEventListener("input", () => {
        searchInput.style.height = 'auto';
        searchInput.style.height = (searchInput.scrollHeight) + 'px';
    });

    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); searchForm.requestSubmit()}});

    chatInput.addEventListener("input", () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });
    
    chatInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); chatSend.click()}});
});