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
from dateutil.parser import parse

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

    now = datetime.datetime.now().isoformat()

    system_message = f"""
    You are "ScheduleBot," an automated personal assistant that translates user requests into structured JSON commands for a Google Calendar system.
    Your ONLY job is to translate the user's request into a single, valid JSON object with the following structure:
    {{"tool_name": "<name_of_the_tool>", "parameters": {{<parameters_for_the_tool>}}}}

    DO NOT add any conversational text or explanations outside of the JSON object.

    --- IMPORTANT RULES ---
    1. You have NO ACCESS to the user's calendar. Do NOT pretend you can check for conflicts or look up event details. Your job is only to create the correct JSON command to ask the system to do something.
    2. If a user wants to change or delete an event, you must ALWAYS use the "find_event" tool first to let the system locate the event.
    3. You MUST use the current date and time to resolve all relative requests (e.g., "tomorrow", "next week"). The current date and time is: {now} (in UTC).
    4. When creating or updating an event, you MUST include the "timeZone" parameter. Unless the user specifies a different timezone, assume all events should be created in the "Europe/Berlin" timezone
    5. All 'dateTime' fields MUST be in RFC3339 format (e.g., 'YYYY-MM-DDTHH:MM:SS').

    --- AVAILABLE TOOLS ---

    1. tool_name: "create_event"
        - Use this to create a new event.
        - parameters: {{
            "summary": "<string>",
            "description": "<string, optional>",
            "location": "<string, optional>",
            "start": {{
                "dateTime": "<The start time in YYYY-MM-DDTHH:MM:SS format>",
                "timeZone": "<The IANA Time Zone string, e.g., 'Europe/Berlin'>"
            }},
            "end": {{
                "dateTime": "<The end time in YYYY-MM-DDTHH:MM:SS format>",
                "timeZone": "<The IANA Time Zone string, e.g., 'Europe/Berlin'>"
            }}
        }}

    2. tool_name: "find_event"
        - Use this when the user wants to get details about, update, or delete an event.
        - parameters: {{
            "query": "<The user's description of the event, e.g., 'dentist appointment' or '3pm meeting'>",
            "timeMin": "<The start of the search window in YYYY-MM-DDTHH:MM:SS format>",
            "timeMax": "<The end of the search window in YYYY-MM-DDTHH:MM:SS format>"
        }}

    3. tool_name: "delete_event"
        - Use this ONLY to delete an event when you ALREADY have the event_id.
        - parameters: {{
            "event_id": "<The specific ID of the event to delete>"
        }}

    4. tool_name: "update_event"
        - Use this ONLY to update an event when you ALREADY have the event_id.
        - parameters: {{
            "event_id": "<The specific ID of the event to update>",
            "summary": "<string, optional>",
            "description": "<string, optional>",
            "start": {{
                "dateTime": "<The new start time in YYYY-MM-DDTHH:MM:SS format>",
                "timeZone": "<The new IANA Time Zone string>"
            }},
            "end": {{
                "dateTime": "<The new end time in YYYY-MM-DDTHH:MM:SS format>",
                "timeZone": "<The new IANA Time Zone string>"
            }}
        }}

    5. tool_name: "reply_text"
        - Use this for any request that is not an action, like a greeting, a question, or if you cannot understand the request.
        - parameters: {{
            "text": "<A friendly, helpful text response to the user>"
        }}
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

    try:
        parsed = json.loads(cleaned)
        tool_name = parsed.get("tool_name")
        parameters = parsed.get("parameters", {})

        result = None

        if tool_name == "find_event":
            find_model = FindEventRequest(**parameters)
            time_min = find_model.time_min
            time_max = find_model.time_max
            found_events_models = find_event_action(app_context, time_min, time_max, find_model)

            events_as_dicts = [model.model_dump(by_alias=True) for model in found_events_models]
            
            result = events_as_dicts

        elif tool_name == "create_event":
            create_model = EventCreateRequest(**parameters)
            create_event_model = create_event_action(app_context, create_model)

            result = create_event_model

        elif tool_name == "delete_event":
            delete_model = DeleteEventRequest(**parameters)
            delete_event_model = delete_event_action(app_context, delete_model) 

            result = delete_event_model

        elif tool_name == "update_event":
            update_model = EventUpdateRequest(**parameters)
            update_event_model = update_event_action(app_context, update_model)

            result = update_event_model

        return jsonify(result)
    
    except (json.JSONDecodeError, AttributeError):
        # If the AI return plain text
        return jsonify({"text":cleaned})
    
    except ValidationError as e:
        # If the AI's parameters are wrong 
        return jsonify({"message": "Invalid parameters form AI.", "details": e.errors()}), 400
    
    except Exception as e:
        # General catch-all for other error
        print (f"An unexpected error occurred: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500

@app.route('/')
def home():
    """ Serve the index.html file. """
    return render_template('index.html')

# --- RUN THE APP ---

if __name__ == '__main__':
    app.run(debug=True)