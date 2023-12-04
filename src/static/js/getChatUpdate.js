// Simulated frontend data, replace with actual implementation
let currentTokenId = 0;
const name = document.getElementById("name").value;

function scrollToBottom() {
  var element = document.getElementById("messageContainer");
  element.scrollTop = element.scrollHeight - element.clientHeight;
}

async function getMessages(tokenId) {
  var parcel = {
    token_id: tokenId,
    tournament: document.getElementById("tID").value,
  };

  const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

  const response = await fetch(
    "http://127.0.0.1:8000/api/tournaments/chat/feed/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(parcel),
    }
  );

  const data = await response.json();

  return data;
}

async function updateView(tokenId) {
  const messagesFromBackend = await getMessages(tokenId);

  if (messagesFromBackend != null) {
    const messageContainer = document.getElementById("messageContainer");

    for (let i = 0; i < messagesFromBackend.length; i++) {
      const message = messagesFromBackend[i];
      if (message.update_on != null) {
        const messageElement = document.getElementById(message.update_on);
        messageElement.firstChild.textContent = getMessageText(message);
        messageElement.firstChild.id = message.token_id;
        if (message.sender == name) {
          if (message.content === null) {
            messageElement.firstChild.classList.remove("message");
          } else {
            messageElement.firstChild.classList.add("message");
          }
        }
      } else {
        const messageElement = document.createElement("div");
        messageElement.style.display = "flex";
        var left = document.createElement("div");

        left.textContent = getMessageText(message);
        left.style.fontSize = "20px";

        messageElement.appendChild(left);
        messageElement.id = message.token_id;

        if (message.sender == name) {
          left.classList.add("message");
        }
        messageContainer.appendChild(messageElement);
      }
    }
    if (messagesFromBackend.length > 0) {

      currentTokenId =
        messagesFromBackend[messagesFromBackend.length - 1].token_id;

      scrollToBottom();
    }
  }
}

function getMessageText(message) {
  if (message.content !== null) {
    return message.sender + ": " + message.content;
  } else {
    return message.sender + ": Message Deleted";
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
        deleteButton.parentNode.firstChild.classList.remove("message");
        deleteButton.remove();
      });

      event.target.parentNode.appendChild(deleteButton);
    }
  });

function deleteMessage(tokenId) {
  const email = document.getElementById("email").value;
  const tID = document.getElementById("tID").value;
  const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

  if (message != "") {
    var messageData = {
      sender: email,
      content: null,
      update_on: tokenId,
      tournament: tID,
    };

    fetch("http://127.0.0.1:8000/api/tournaments/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(messageData),
    });
  }


}

updateView(currentTokenId);

setInterval(() => {
  updateView(currentTokenId);
}, 1000);
