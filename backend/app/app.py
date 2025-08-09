import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
from pathlib import Path

# Load environment variables from .env file
script_dir = Path(__file__).parent
base_dir = script_dir.parent.parent
dotenv_path = base_dir / 'env' / 'production.env'
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)
CORS(app)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


# --- AI LOGIC ---

def get_ai_response(user_message):
    """ Sends a message to the OpenAI API and returns the response. """
    try: 
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are BillaBee, a cheerful and helpful assistant who loves bee and honey puns. You help users be productive."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return "Oh, honey! My antennae are a bit fuzzy right now. I couldn't connect to the hive. Please try again later."
    
# --- ROUTES ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    if data is None:
        return jsonify({'response': "No JSON data received."}), 400
    user_message = data.get('message')
    bot_response = get_ai_response(user_message)
    return jsonify({'response': bot_response})

@app.route('/')
def home():
    """ Serve the index.html file. """
    return app.send_static_file('index.html')

# --- RUN THE APP ---

if __name__ == '__main__':
    app.run(debug=True)