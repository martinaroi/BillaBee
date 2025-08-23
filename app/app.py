import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import json
from datetime import datetime
from pathlib import Path
import re
from calendar_service import *
from models import *
from pydantic import ValidationError
from context import *
from action import *

# Load environment variables from .env file
script_dir = Path(__file__).parent
base_dir = script_dir.parent
dotenv_path = base_dir / 'env' / 'production.env'
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)
CORS(app)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app_context = AppContext()

# --- AI LOGIC ---

def get_ai_response(user_message):
    """ Sends a message to the OpenAI API and returns the response. """
    system_message = """
    You are Billa the Bee, a cheerful and helpful personal scheduling assistant. 
    Normally, you respond with friendly text. 
    BUT if the user is asking you to schedule something, 
    Always reply in VALID JSON with this exact structure:
    {
      "response": "<short friendly text to the user>",
      "events": [
        {
          "summary": "<short title>",
          "description": "<optional details>",
          "start": { "dateTime": "<ISO 8601 datetime>", "timeZone": "<valid timezone name>" },
          "end": { "dateTime": "<ISO 8601 datetime>", "timeZone": "<valid timezone name>" }
        }
        ]
    }
    If there are no events, reply with "events": [].
    """
    try: 
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
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
    

def split_json_text(bot_response):
    try:
        parsed = json.loads(bot_response)
        message = parsed.get("response", "")

        return parsed, message
    except json.JSONDecodeError:
        return None, bot_response
    
def clean_json_string(json_str):
    # Remove ```json and ``` if present
    return re.sub(r"```(?:json)?\s*|\s*```", "", json_str).strip() 

# --- ROUTES ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    if data is None:
        return jsonify({'response': "No JSON data received."}), 400
    
    user_message = data.get('message')
    bot_response = get_ai_response(user_message)
    cleaned = clean_json_string(bot_response)

    parsed, message = split_json_text(cleaned)

    if parsed:
        events = parsed.get("events", [])
        response = parsed.get('response', message)
        return jsonify({"response": response, 'events': events})
    else:
        return jsonify({'response': bot_response, 'events': []})
    
@app.route('/api/create_event', methods=['POST'])
def create_event_api():
    # Safety checks remain the same
    if not app_context.calendar_service:
        return jsonify({"status": "error", "message": "Server not configured."}), 503

    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Invalid JSON body."}), 400

    try:
        # 1. Validate the incoming request (This works)
        event_model = EventCreateRequest(**data)
        
        # 2. Perform the action (This works, and the event is created)
        created_event_dict = create_event_action(app_context, event_model)

        # 3. --- THIS IS THE GUARANTEED FIX ---
        # Instead of trying to sanitize the whole Google object, we build a new,
        # simple dictionary with only the safe data we need.
        
        simple_response_event = {
            "summary": created_event_dict.get("summary"),
            "description": created_event_dict.get("description"),
            "htmlLink": created_event_dict.get("htmlLink"),
            
            # The 'start' and 'end' objects from the API response contain
            # simple strings, which are safe for JSON.
            "start": created_event_dict.get("start"),
            "end": created_event_dict.get("end")
        }

        # 4. We pass this new, simple, guaranteed-safe dictionary to jsonify.
        return jsonify({"status": "success", "event": simple_response_event}), 201

    except ValidationError as e:
        # This error handling is correct
        print(f"!!! PYDANTIC VALIDATION ERROR !!!\n{e.json()}\n!!! END OF ERROR !!!")
        return jsonify({
            "status": "error", 
            "message": "Invalid data provided", 
            "details": e.errors()
        }), 400
    
    except Exception as e:
        # This error handling is correct
        print(f"!!! AN UNEXPECTED ERROR OCCURRED: {e} !!!")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/')
def home():
    """ Serve the index.html file. """
    return render_template('index.html')

# --- RUN THE APP ---

if __name__ == '__main__':
    app.run(debug=True)