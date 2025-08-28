import os
from flask import Flask, request, jsonify, render_template, session
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
app.secret_key = os.urandom(24)
CORS(app)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app_context = AppContext()

def load_user_profile(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# --- AI LOGIC ---

def get_tool_user_response(user_message, history = None):
    """ Sends a message to the OpenAI API and returns the response. """

    now = datetime.datetime.now().isoformat()

    system_message = f"""
    You are "ScheduleBot," an automated personal assistant that translates user requests into structured JSON commands for a Google Calendar system.
    Your ONLY job is to translate the user's request into a single, valid JSON object with the following structure:
    {{"tool_name": "<name_of_the_tool>", "parameters": {{<parameters_for_the_tool>}}}}
    Your goal is to find the single best tool to match the user's instruction.
    If the instruction is a greeting or something that is not a tool, you can use "reply_text".
    However, if the instruction mentions finding, creating, deleting, or updating something on the calendar, you MUST use the corresponding tool.

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
        messages = list(history) if history else []

        messages.insert(0, {"role": "system", "content": system_message})

        messages.append({"role": "user", "content": user_message})

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return "Oh, honey! My antennae are a bit fuzzy right now. I couldn't connect to the hive. Please try again later."
    
def get_personal_assistant_response(user_message, user_profile, history=None):

    priorities_text = "\n- ".join(user_profile['priorities'])

    personal_assistant_prompt = f"""
    You are Billa the Bee, a friendly and proactive personal assistant for {user_profile['name']}. 
    Your goal it to help the user plan their perfect productive day.
    
    --- {user_profile['name']}'s Personal Informatoin ---
    - Timezone: {user_profile['timezone']}
    - Typical Work Hours: {user_profile['work_hours']['start']} to {user_profile['work_hours']['end']}
    - Priorities:
    - {priorities_text}

    --- Your Task ---
    Your core task is to act as the user's planning partner. You operate in a multi-step loop. For every user message, you must follow these steps and decide on a single action.

    **1. Analyze the User's Goal:**
    Read the user's latest message and the conversation history. Combine this with your knowledge of the user's priorities and habits to understand their high-level goal (e.g., "plan my day," "find free time," "prepare for tomorrow").

    **2. Think Step-by-Step (Your Internal Monologue):**
    Before you respond, reason about the situation.
    - Do I have all the information I need to fulfill the user's goal?
    - Or do I need to check the user's calendar to see what events already exist?

    **3. Decide Your Response (This is the most important step):**
    Based on your thinking, choose **one** of the following two response types.

    **A) If you NEED information from the calendar:**
    - Your ONLY response should be a simple, clear sentence stating your intention. This sentence will be intercepted by a tool-using system that will fetch the information for you.
    - **Do NOT** talk to the user. State your internal goal.
    - **Do NOT** create JSON.
    - **Examples of valid responses in this mode:**
        - "Okay, first I need to check the calendar to see all the events for this Wednesday."
        - "I should check the user's calendar for tomorrow to see if there are any conflicts."
        - "I need to find the 'Workout' event the user mentioned to confirm its time."

    **B) If you have ALL the information you need:**
    - Your response MUST start with the special phrase "FINAL ANSWER:".
    - After the phrase, write your friendly, conversational message directly to the user.
    - Ask for the user's agreement or feedback.
    - If the user just says "hello" or asks a simple question, just have a normal conversation.
    - **Examples of valid responses in this mode:**
        - "FINAL ANSWER: Okay, I see your workout is at 7pm. Since your thesis is the top priority, how about we schedule a focus block for it from 2pm to 5pm? Does that sound good?"
        - "FINAL ANSWER: It looks like your morning is free. I'd suggest working on your thesis from 9am to 12pm, which leaves your afternoon open for other tasks."
        - "FINAL ANSWER: You asked about tomorrow. You have a 'Dentist Appointment' at 10am and 'Project Sync' at 2pm."
    
    **4. Act on User Agreement:**
    - After you have proposed a plan and the user agrees (e.g., they say "yes", "sounds good", "perfect"), your next job is to execute that plan.
    - You must break down the plan into a series of simple, one-at-a-time instructions for the tool-using system.
    - Your response should be the **first instruction** in the sequence.
    - **Example Execution Instruction:** "Okay, now I will create an event for 'Thesis Work' from 2pm to 5pm today."
    """

    messages = list(history) if history else[]

    messages.insert(0, {"role": "system", "content": personal_assistant_prompt})

    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.chat.completions.create(
            model = "gpt-4o", 
            messages=messages, 
            temperature=0.7, 
            max_tokens=250
        )
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
    
    except Exception as e:
        print(f"Error communicating with OpenAI (Personal Assistant): {e}")
        return "Oh dear, my bee-brain is buzzing with an error. Please try again."


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

def execute_tool(tool_json_str):
    """
    Parses a JSON string, identifies the tool, and executes the corresponding action.
    Returns the result of the action.
    """
    try:
        cleaned = clean_json_string(tool_json_str)
        parsed = json.loads(cleaned)
        tool_name = parsed.get("tool_name")
        parameters = parsed.get("parameters", {})

        if tool_name == "find_event":
            find_model = FindEventRequest(**parameters)
            time_min = find_model.time_min
            time_max = find_model.time_max
            found_events_models = find_event_action(app_context, time_min, time_max, find_model)
            events_as_dicts = [model.model_dump(by_alias=True) for model in found_events_models]
            return events_as_dicts

        elif tool_name == "create_event":
            create_model = EventCreateRequest(**parameters)
            create_event_model = create_event_action(app_context, create_model)
            return create_event_model

        elif tool_name == "delete_event":
            delete_model = DeleteEventRequest(**parameters)
            delete_event_model = delete_event_action(app_context, delete_model) 
            return delete_event_model

        elif tool_name == "update_event":
            update_model = EventUpdateRequest(**parameters)
            update_event_model = update_event_action(app_context, update_model)
            return update_event_model

        else:
            return {"error": f"Unknow tool name: {tool_name}"}
        
    except ValidationError as e:
        # If the AI's parameters are wrong 
        return {"error": "Invalid parameters from AI.", "details": e.errors()}
        
    except Exception as e:
        # General catch-all for other error
        print(f"!!! An unexpected error occurred in execute_tool: {e} !!!")
        return {"error": "An internal server error occurred during tool execution."}
    
def json_datetime_serializer(obj):
    """
    This is our custom converter. json.dumps will call this function
    whenever it finds an object it doesn't know how to handle.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def summarize_tool_result(tool_name, tool_result):
    """
    Summarizes the result of a tool to only include essential information
    for the AI's memory.
    """
    if tool_name == "find_event" and isinstance(tool_result, list):
        summary = []
        for event in tool_result:
            summary.append({
                "summary": event.get("summary"),
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime")
            })
        return summary
    else:
        return tool_result
  

# --- ROUTES ---
@app.route('/api/select_user', methods=['POST'])
def set_user():
    data = request.json
    if data is None:
        return jsonify({"status": "error", "message": "No JSON data received."}), 400
    
    username = data.get('username')

    if not username: 
        return jsonify({"status": "error", "message": "Username is required."}), 400
    
    # Store the selected username in the session
    session['current_user'] = username
    print(f"Session user set to: {username}")

    return jsonify({f"User context switched to {username}"})


@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    if data is None: 
        return jsonify({'response': "No JSON data received."}), 400
    
    username = session.get('current_user', 'Martina')
    profile_filename = f"user_profile_{username}.json"

    try:
        user_profile = load_user_profile(profile_filename)
    except FileNotFoundError:
        return jsonify({f"Profile for user '{username}' not found."}), 404
    
    history = session.get('chat_history', [])
    user_message = data.get('message')
    history.append({"role": "user", "content": user_message})

    for _ in range(5): 
        
        pa_response = get_personal_assistant_response(user_message, user_profile, history=history)
        history.append({"role": "assistant", "content": pa_response})

        if "FINAL ANSWER:" in pa_response:
            print("--- PA has a final answer. Ending loop. ---")
            final_message = pa_response.replace("FINAL ANSWER:", "").strip()
            session['chat_history'] = history
            return jsonify({
                "status": "success",
                "tool_name": "reply_text",
                "data": {"text": final_message}
            })
        
        is_tool_request = "check the calendar" in pa_response.lower() or \
                          "find the event" in pa_response.lower() or \
                          "create an event" in pa_response.lower() or \
                          "delete the event" in pa_response.lower() or \
                          "update the event" in pa_response.lower()
        
        if is_tool_request:
            print(f"--- PA wants to use a tool: '{pa_response}' ---")
            tool_json_str = get_tool_user_response(pa_response)

            try:
                tool_name = json.loads(clean_json_string(tool_json_str)).get("tool_name")
            except (json.JSONDecodeError, AttributeError):
                tool_name = None

            tool_result = execute_tool(tool_json_str)
            print(f"--- Tool Result: {tool_result} ---")

            if isinstance(tool_result, dict) and "error" in tool_result:
                return jsonify({"status": "error", "message": "A tool failed to execute.", "details": tool_result})
            
            summarized_result = summarize_tool_result(tool_name, tool_result)
            history.append({
                "role": "assistant",
                "content": f"OBSERVATION: {json.dumps(summarized_result, default=json_datetime_serializer)}"
            })
            continue
        
        else:
            print("--- PA has finished executing. Ending loop. ---")
            session['chat_history'] = history
            return jsonify({
                "status": "success",
                "tool_name": "reply_text",
                "data": {"text": pa_response}
            })
        
    return jsonify({"status": "error", "message": "The assistant took too many steps. Please try again."})


@app.route('/')
def home():
    """ Serve the index.html file. """
    return render_template('index.html')


# --- RUN THE APP ---
if __name__ == '__main__':
    app.run(debug=True)