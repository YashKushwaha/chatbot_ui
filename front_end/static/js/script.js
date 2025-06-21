const inputBox = document.getElementById("user-input-div");
const chatHistory = document.getElementById("chat-history");

inputBox.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault(); // prevent newline

    const message = inputBox.innerText.trim();
    if (!message) return;

    // 1. Add to chat history
    const newMsg = document.createElement("div");
    newMsg.className = "user-message";
    newMsg.textContent = message;
    chatHistory.appendChild(newMsg);
    inputBox.innerText = "";

    // Scroll to bottom
    const scrollContainer = document.getElementById("chat-history-container");
    scrollContainer.scrollTop = scrollContainer.scrollHeight;

    // 2. Clear input
   

    // 3. Send to backend
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();
      console.log("Server replied:", data);
      // You can append server's response to chatHistory here if needed
    } catch (err) {
      console.error("Send failed", err);
    }
  }
});
