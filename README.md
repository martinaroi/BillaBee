# 🐝 Hive of BillaBee - Your Personal AI Calendar Assistant

BillaBee is a conversational AI assistant designed to help you plan your perfect day and manage your Google Calendar through natural language. It understands your personal priorities, work habits, and can have context-aware conversations to schedule, find, and manage your events.
---

## ✨ Features

*   **Conversational Day Planning:** Tell BillaBee your goals for the day, and it will create a schedule for you based on your predefined priorities and existing calendar events.
*   **Full Google Calendar Integration:**
    *   **Create** new events with natural language ("Schedule a meeting tomorrow at 3pm").
    *   **Read** existing events ("What's on my calendar for Friday?").
    *   **Update** events in a conversational flow.
    *   **Delete** events with simple follow-up commands ("Okay, cancel that meeting").
*   **Personalized for You:** Using a simple configuration file, BillaBee knows your work hours, priorities, and timezone to create schedules that are truly tailored to you.

---

## 🛠️ Tech Stack

*   Backend: Python (Flask), Pydantic, Flask-CORS
*   AI: OpenAI API (GPT-4o)
*   Calendar: Google Calendar API (google-api-python-client)
*   Frontend: HTML, CSS, JavaScript
*   Markdown rendering (bot replies): marked.js + DOMPurify (CDN) for safe HTML

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

*   Python 3.8+
*   A Google Account with Google Calendar enabled.
*   An OpenAI API Key.

### 1. Clone the Repository

```bash
git clone https://github.com/martinaroi/BillaBee.git
cd BillaBee
```

### 2. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

*   **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies

This repo includes a pyproject with dependencies. You can either use pip with a requirements.txt (simple) or Poetry (optional).

Option A — pip (simple)
1) Create a venv (see above), then install the needed packages:
    - flask, flask-cors, openai, python-dotenv, pydantic, google-api-python-client, google-auth-httplib2, google-auth-oauthlib
2) (Optional) Freeze them for reuse:
```bash
pip freeze > requirements.txt
```

Option B — Poetry (advanced)
```bash
pip install poetry
poetry install
```

### 4. Configuration

You will need to set up a few configuration files. **These files contain sensitive information and should NOT be committed to GitHub.** The project's `.gitignore` file is already set up to ignore them.

**a) Google Calendar API Credentials**

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  Enable the "Google Calendar API" for your project.
3.  Create credentials for a "Desktop app".
4.  Download the credentials JSON file and place it at `app/credentials.json`.
5.  The first time you run the application, it will open a browser window asking you to authorize access to your calendar. After you approve, a `app/token.json` file will be created.

**b) OpenAI API Key**

Set your key in `env/production.env` (loaded automatically by the app):
```
OPENAI_API_KEY="your_secret_api_key_here"
```

**c) Your Personal Profile**

Profiles live in `app/`. Use the example provided:
```bash
cp app/user_profile.json.example app/user_profile_<YourName>.json
```
Fill it with your timezone, priorities, anchors, etc. You can switch users from the UI.

### 5. Run the Application

Start the Flask server from the `app/` directory:

```bash
cd app
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

If you run from the project root, set FLASK_APP accordingly or ensure your working directory is `app/`.

---

## 🧭 UI/UX Notes

- Search and chat inputs auto-expand (textarea) and support:
    - Enter to submit/send, Shift+Enter for a new line
- Bee icons in the header return to the home screen from chat
- Google Calendar link is available on the welcome screen and inside the chat input row
- Bot replies support Markdown (bold, lists, code blocks) and are sanitized client-side

## 🎨 Themed Event Colors

When confirming events, you can select a theme (Work, Study, Exercise, Health, Wellbeing, Family, Social, Errand, Focus). The backend maps themes to Google Calendar color IDs automatically on create/update. You can customize this mapping in `app/action.py`.

---

## 🔐 Security & Tips

- Never commit real `credentials.json`, `token.json`, or API keys.
- This app loads environment variables from `env/production.env`.
- If OAuth fails, delete `app/token.json` and re-run to re-auth.

## 🧩 Troubleshooting

- Missing packages: install via pip or Poetry (see Install Dependencies)
- CORS errors: ensure Flask-CORS is installed and enabled (already configured)
- Google API 403/401: check credentials, scopes, and that the correct Google account is used

---

## 💬 How to Use

Start chatting with BillaBee! Here are some examples:

*   **Simple Creation:** "I need to schedule a dentist appointment for next Tuesday at 10am."
*   **Finding Events:** "What's on my calendar for this weekend?"
*   **Conversational Deletion:**
    *   You: "Find my 3pm meeting tomorrow."
    *   BillaBee: (Shows you the meeting details)
    *   You: "Okay, please cancel it."
*   **Day Planning:** "I need to work on my thesis today. I also have a workout planned for the evening. Can you help me plan my day?"

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
