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
    """Root route to confirm the AI Mentor is live."""
    return "🚀 HMHustleRightNow AI Mentor is Live!"

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
        # Extract AI's response
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
