// Simulated frontend data, replace with actual implementation
let currentTokenId = 0;
const name = document.getElementById("name").value;

const fakeMessage = [
  [{ tokenId: 1, updateOn: null, content: "Hello, World!", sender: "Alice" }],
  [{ tokenId: 2, updateOn: 1, content: "Updated message!", sender: "Alice" }],
  [
    { tokenId: 3, updateOn: 2, content: null, sender: "Alice" },
  ],
  [{ tokenId: 4, updateOn: null, content: "New message!", sender: "Bob" }],
  [{ tokenId: 5, updateOn: 4, content: "Updated message!", sender: "Bob" }],
  [{ tokenId: 6, updateOn: null, content: "New Message 1", sender: "test1" }],
  [{ tokenId: 7, updateOn: null, content: "New Message 2", sender: "Bob" }],
  [{ tokenId: 8, updateOn: null, content: "New Message 3", sender: "test1" }],
  [{ tokenId: 9, updateOn: null, content: "New Message 4", sender: "Bob" }],
  [{ tokenId: 10, updateOn: null, content: "New Message 5", sender: "Bob" }],
  [{ tokenId: 11, updateOn: null, content: "New Message 6", sender: "Bob" }],
  [{ tokenId: 12, updateOn: null, content: "New Message 7", sender: "Bob" }],
  [
    { tokenId: 13, updateOn: 12, content: null, sender: "Bob" },
  ],
  [{ tokenId: 14, updateOn: null, content: "New Message 8", sender: "Bob" }],
  [{ tokenId: 15, updateOn: null, content: "New Message 9", sender: "Bob" }],
  [{ tokenId: 16, updateOn: null, content: "New Message 10", sender: "Bob" }],
  [{ tokenId: 17, updateOn: null, content: "New Message 11", sender: "Bob" }],
  [{ tokenId: 18, updateOn: null, content: "New Message 12", sender: "Bob" }],
  [{ tokenId: 19, updateOn: null, content: "New Message 13", sender: "Bob" }],
  [{ tokenId: 20, updateOn: null, content: "New Message 14", sender: "Bob" }],
  [{ tokenId: 21, updateOn: null, content: "New Message 15", sender: "Bob" }],
  [{ tokenId: 22, updateOn: null, content: "New Message 16", sender: "Bob" }],
  [{ tokenId: 23, updateOn: null, content: "New Message 17", sender: "Bob" }],
  [{ tokenId: 24, updateOn: null, content: "New Message 18", sender: "Bob" }],
  [{ tokenId: 25, updateOn: null, content: "New Message 19", sender: "Bob" }],
  [{ tokenId: 26, updateOn: null, content: "New Message 20", sender: "Bob" }],
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

function updateView(tokenId) {
  const messagesFromBackend = getMessages(tokenId);
  if (messagesFromBackend != null) {
    const messageContainer = document.getElementById("messageContainer");

    for (let i = 0; i < messagesFromBackend.length; i++) {
      const message = messagesFromBackend[i];
      if (message.updateOn != null) {
        const messageElement = document.getElementById(message.updateOn);

        messageElement.firstChild.textContent = getMessageText(message);
        messageElement.firstChild.id = message.tokenId;
      } else {
        const messageElement = document.createElement("div");
        messageElement.style.display = "flex";
        var left = document.createElement("div");

        left.textContent = getMessageText(message);
        left.style.fontSize = "20px";

        messageElement.appendChild(left);
        messageElement.id = message.tokenId;

        if (message.sender == name) {
          left.classList.add("message");
        }

        messageContainer.appendChild(messageElement);
      }
    }
    currentTokenId =
      messagesFromBackend[messagesFromBackend.length - 1].tokenId;
    scrollToBottom();
  }
}

function getMessageText(message) {
  if (message.content !== null) {
    return message.sender + ": " + message.content;
  } else {
    return (
      message.sender + ": " + `Message ${message.tokenId} deleted`
    );
  }
}

document
  .getElementById("messageContainer")
  .addEventListener("click", function (event) {
    if (event.target.classList.contains("message")) {

      document.querySelectorAll(".delete-button").forEach((button) => {
        button.parentNode.style.backgroundColor = "white";
        button.remove();
      });

      event.target.parentNode.style.backgroundColor = "#e0e0e0";

      var deleteButton = document.createElement("button");
      deleteButton.textContent = "Delete";
      deleteButton.classList.add("delete-button");
      deleteButton.style.marginLeft = "10px";

      deleteButton.addEventListener("click", function () {
        const tokenId = event.target.parentNode.id;
        deleteMessage(tokenId);
        deleteButton.parentNode.style.backgroundColor = "white";
        deleteButton.remove();
      });

      event.target.parentNode.appendChild(deleteButton);

    }
  });

function deleteMessage(tokenId){
  const email = document.getElementById("email").value;
  const tID = document.getElementById("tID").value;
  const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

  if (message != "") {

      var messageData ={
          "sender": email,
          "content": null,
          "update_on": tokenId,
          "tournament": tID
      }

      fetch("http://127.0.0.1:8000/api/tournaments/chat/", {
          method: "POST",
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
          },
          body: JSON.stringify(messageData),
      })

  }

  console.log(messageData);
}

updateView(currentTokenId);

setInterval(() => {
  updateView(currentTokenId);
  // scrollToBottom();
}, 2000);
