const inputBox = document.getElementById("user-input-div");
const chatHistory = document.getElementById("chat-history");
const scrollContainer = document.getElementById("chat-history-container");

// Utility: Scroll to bottom of chat
function scrollToBottom(scrollContainer) {
  scrollContainer.scrollTop = scrollContainer.scrollHeight;
}

// Utility: Create and append a user message
function appendUserMessage(message, chatHistory) {
  const newMsg = document.createElement("div");
  newMsg.className = "user-message";
  newMsg.textContent = message;
  chatHistory.appendChild(newMsg);
}

// Utility: Append server response
function appendServerMessage(reply, chatHistory) {
  const replyMsg = document.createElement("div");
  replyMsg.className = "server-message";
  replyMsg.textContent = reply;
  chatHistory.appendChild(replyMsg);
  scrollToBottom(scrollContainer);
}

// Utility: Send message to backend
async function sendMessageToBackend(message, chatHistory) {
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    console.log("Server replied:", data);

    // Optional: Display server's reply
    if (data.response) {
      appendServerMessage(data.response, chatHistory);
    }
  } catch (err) {
    console.error("Send failed", err);
  }
}



async function handleUserInput(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();

    const message = inputBox.innerText.trim();
    if (!message) return;

    appendUserMessage(message, chatHistory);
    inputBox.innerText = "";
    scrollToBottom(scrollContainer);

    await sendMessageToBackend(message, chatHistory);
  }
}

// Main input handler
inputBox.addEventListener("keydown", handleUserInput);