from flask import Flask, request, jsonify
import openai
import os
import logging
from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY)
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure Logging
logging.basicConfig(
    filename="mentor.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Create Flask app
app = Flask(__name__)

# Execution-focused prompt
PROMPT_STYLE = """
You are HM Hustle AI, a no-BS execution mentor.
Your mission: **Force the user to take action.**
- If they overthink, simplify it.
- If they hesitate, call them out.
- If they lack direction, give them **one single action step.**
- Keep it short, fast, and impactful.
"""

@app.route("/")
def home():
    """Root route to show a simple web page for the AI Mentor."""
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <!-- Make it responsive on mobile -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>HMHustleRightNow AI Mentor</title>
        <style>
          body {
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
          }
          .container {
            max-width: 600px; 
            margin: 40px auto; 
            background: #fff; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
          }
          h1 {
            margin-bottom: 0.5rem;
          }
          textarea {
            width: 100%; 
            padding: 10px; 
            border-radius: 4px; 
            border: 1px solid #ccc;
          }
          button {
            background: #7e57c2; 
            color: #fff; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            margin-top: 10px;
          }
          button:hover {
            background: #6d4ead;
          }
          #response {
            margin-top: 1rem; 
            white-space: pre-wrap; 
            border: 1px solid #ccc; 
            padding: 10px; 
            border-radius: 4px;
            min-height: 50px;
            background-color: #fafafa;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚀 HMHustleRightNow AI Mentor</h1>
          <p>Type your question or request, and the AI Mentor will push you to take action!</p>
          <textarea id="message" rows="5" placeholder="Enter your message..."></textarea><br><br>
          <button onclick="sendRequest()">Send</button>
          
          <h2>Response:</h2>
          <div id="response"></div>
        </div>

        <script>
          async function sendRequest() {
            const userMessage = document.getElementById('message').value;
            if(!userMessage.trim()) {
              alert("Please enter a message first!");
              return;
            }
            
            const responseDiv = document.getElementById('response');
            responseDiv.textContent = "Thinking...";

            try {
              const res = await fetch('/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
              });
              const data = await res.json();
              if (data.response) {
                responseDiv.textContent = data.response;
              } else if (data.error) {
                responseDiv.textContent = "Error: " + data.error;
              }
            } catch (err) {
              responseDiv.textContent = "Network error or server issue.";
            }
          }
        </script>
      </body>
    </html>
    """

@app.route("/execute", methods=["POST"])
def execute():
    """Handles incoming requests and provides execution-based AI responses."""
    data = request.get_json()
    user_input = data.get("message") if data else ""

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Generate AI response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": PROMPT_STYLE},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response.choices[0].message.content.strip()

        # Log request & response
        logging.info(f"USER: {user_input} | AI: {ai_response}")

        return jsonify({"response": ai_response})

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": "OpenAI API request failed."}), 500

    except Exception as e:
        logging.error(f"General Error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    # Use PORT from environment if available (e.g., on Render/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
