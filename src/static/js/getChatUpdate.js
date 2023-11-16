// Simulated frontend data, replace with actual implementation
let currentTokenId = 0; // Assume the frontend starts with token ID 0

const fakeMessage = [
  [{ tokenId: 1, updateOn: null, content: "Hello, World!", sender: "Alice" }],
  [{ tokenId: 2, updateOn: 1, content: "Updated message!", sender: "Alice" }],
  [
    { tokenId: 3, updateOn: 2, content: null, sender: "Alice" }, // Deleted message
  ],
  [{ tokenId: 4, updateOn: null, content: "New message!", sender: "Bob" }],
  [{ tokenId: 5, updateOn: 4, content: "Updated message!", sender: "Bob" }],
  [{ tokenId: 6, updateOn: null, content: "New Message 1", sender: "Bob" }],
  [{ tokenId: 7, updateOn: null, content: "New Message 2", sender: "Bob" }],
  [{ tokenId: 8, updateOn: null, content: "New Message 3", sender: "Bob" }],
  [{ tokenId: 9, updateOn: null, content: "New Message 4", sender: "Bob" }],
  [{ tokenId: 10, updateOn: null, content: "New Message 5", sender: "Bob" }],
  [{ tokenId: 11, updateOn: null, content: "New Message 6", sender: "Bob" }],
  [{ tokenId: 12, updateOn: null, content: "New Message 7", sender: "Bob" }],
];

function scrollToBottom() {
  var element = document.getElementById("messageContainer");
  element.scrollTop = element.scrollHeight - element.clientHeight;
}

function getMessages(tokenId) {
  try {
    const message = fakeMessage[tokenId];
    return message;
  } catch (err) {
    console.log(err);
    return null;
  }
}

// Function to simulate receiving messages from the backend
function updateView(tokenId) {
  // Simulated backend response, replace with actual API call
  // Here, we assume messages are hardcoded for demonstration purposes

  const messagesFromBackend = getMessages(tokenId);
  if (messagesFromBackend == null) {
    console.log("No new messages");
  } else {
    const messageContainer = document.getElementById("messageContainer");

    for (let i = 0; i < messagesFromBackend.length; i++) {
      const message = messagesFromBackend[i];
      if (message.updateOn != null) {
        // modify the message in message Container that has the same tokenId as updateOn
        const messageElement = document.getElementById(message.updateOn);
        messageElement.textContent = getMessageText(message);
        messageElement.id = message.tokenId;
      } else {
        // create a new message
        const messageElement = document.createElement("div");
        messageElement.textContent = getMessageText(message);
        messageElement.id = message.tokenId;
        messageElement.style.fontSize = "20px";
        messageContainer.appendChild(messageElement);
      }
    }

    // Update the current token ID
    console.log(messagesFromBackend[messagesFromBackend.length - 1].tokenId);
    currentTokenId =
      messagesFromBackend[messagesFromBackend.length - 1].tokenId;
  }
}

// Function to format message text for display
function getMessageText(message) {
  if (message.content !== null) {
    return "From " + message.sender + ": " + message.content;
  } else {
    return (
      "From " + message.sender + ": " + `Message ${message.tokenId} deleted`
    );
  }
}

// Simulate initial message retrieval
updateView(currentTokenId);

// Simulate periodic message updates (you may use WebSocket or other real-time mechanisms)
setInterval(() => {
  console.log("Updating messages...");
  updateView(currentTokenId);
  scrollToBottom();
}, 2000); // Update every second, adjust as needed
