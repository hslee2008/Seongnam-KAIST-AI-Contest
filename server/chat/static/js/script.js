document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatWindow = document.getElementById("chat-window");

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage(message, "user-message");
        userInput.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            appendMessage(data.response, "bot-message");

        } catch (error) {
            console.error("Error:", error);
            appendMessage("오류가 발생했습니다.", "bot-message");
        }
    }

    function appendMessage(content, className) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", className);

        if (typeof content === 'string') {
            messageDiv.textContent = content;
        } else if (Array.isArray(content)) {
            content.forEach(event => {
                const eventDiv = document.createElement('div');
                eventDiv.classList.add('event');
                
                const titleLink = document.createElement('a');
                titleLink.href = event.link;
                titleLink.textContent = event.title;
                titleLink.target = "_blank";

                const sourceP = document.createElement('p');
                sourceP.textContent = `출처: ${event.source}`;

                const dateP = document.createElement('p');
                dateP.textContent = `날짜: ${event.date}`;

                eventDiv.appendChild(titleLink);
                eventDiv.appendChild(sourceP);
                eventDiv.appendChild(dateP);
                messageDiv.appendChild(eventDiv);
            });
        } 
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
