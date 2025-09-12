document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatWindow = document.getElementById("chat-window");
    const loadingDiv = document.getElementById("loading");

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
        loadingDiv.style.display = "block";
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            });

            loadingDiv.style.display = "none";

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status}`);
            }

            const data = await response.json();
            console.log("API 응답:", JSON.stringify(data, null, 2));
            appendMessage(data.response, "bot-message");

        } catch (error) {
            console.error("Error:", error);
            loadingDiv.style.display = "none";
            appendMessage("오류가 발생했습니다: " + error.message, "bot-message");
        }
    }

    function appendMessage(content, className) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", className);

        if (typeof content === 'string') {
            messageDiv.textContent = content;
        } else if (content && content.recommended_event && Object.keys(content.recommended_event).length > 0) {
            const event = content.recommended_event;
            const eventDiv = document.createElement('div');
            eventDiv.classList.add('event');

            const titleLink = document.createElement('a');
            titleLink.href = event.link || '#';
            titleLink.textContent = event.title || '제목 없음';
            titleLink.target = "_blank";

            const sourceP = document.createElement('p');
            sourceP.textContent = `기관: ${event.source || '출처 없음'}`;


            eventDiv.appendChild(titleLink);
            eventDiv.appendChild(sourceP);
            messageDiv.appendChild(eventDiv);
        } else {
            messageDiv.textContent = content.reason || "행사를 찾을 수 없습니다.";
        }

        chatWindow.appendChild(messageDiv);

        requestAnimationFrame(() => {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        });
    }
});