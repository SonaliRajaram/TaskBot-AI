function toggleChatbox() {
    const chatbox = document.getElementById('chatbot');
    chatbox.classList.toggle('hidden');
}

let sessionId = Date.now();
    
        function sendMessage() {
            let userInput = document.getElementById("userInput").value;
            if (!userInput.trim()) return;
    
            document.getElementById("chatbox").innerHTML += `<p class='user'>You: ${userInput}</p>`;
            document.getElementById("userInput").value = "";
    
            fetch("http://127.0.0.1:5000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId, message: userInput })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("chatbox").innerHTML += `<p class='bot'>Bot: ${data.response}</p>`;
            });
        }

        document.getElementById("userInput").addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }
        });
