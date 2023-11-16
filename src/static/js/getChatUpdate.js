// Simulated frontend data, replace with actual implementation
let currentTokenId = 0; // Assume the frontend starts with token ID 0

// Function to simulate receiving messages from the backend
function getMessages(tokenId) {
    // Simulated backend response, replace with actual API call
    // Here, we assume messages are hardcoded for demonstration purposes
    const messagesFromBackend = [
        { tokenId: 1, updateOn: null, content: "Hello, World!" },
        { tokenId: 2, updateOn: 1, content: "Updated message!" },
        { tokenId: 3, updateOn: 2, content: null }, // Deleted message
        { tokenId: 4, updateOn: null, content: "New message!" },
    ];

    // Filter messages based on the provided tokenId
    const filteredMessages = messagesFromBackend.filter(message => message.tokenId > tokenId);

    // Update the frontend's currentTokenId
    currentTokenId = Math.max(...messagesFromBackend.map(message => message.tokenId));

    // Process the filtered messages and update the UI
    updateUI(filteredMessages);
}

// Function to update the UI with messages
function updateUI(messages) {
    const messageContainer = document.getElementById("messageContainer");

    // Update or create elements based on the messages
    messages.forEach(message => {
        const messageElement = document.createElement("div");
        messageElement.textContent = getMessageText(message);
        messageContainer.appendChild(messageElement);
    });
}

// Function to format message text for display
function getMessageText(message) {
    if (message.content !== null) {
        return message.content;
    } else {
        return `Message ${message.tokenId} deleted`;
    }
}

// Simulate initial message retrieval
getMessages(currentTokenId);

// Simulate periodic message updates (you may use WebSocket or other real-time mechanisms)
setInterval(() => {
    getMessages(currentTokenId);
}, 1000); // Update every 5 seconds, adjust as needed
