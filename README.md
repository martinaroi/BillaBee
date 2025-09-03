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

*   **Backend:** Python with Flask
*   **AI Engine:** OpenAI API (GPT-4o)
*   **Calendar Service:** Google Calendar API
*   **Frontend:** HTML, CSS, JavaScript

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

Install all the necessary Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```
*(**Note:** If you don't have a `requirements.txt` file, you can create one after installing your libraries by running `pip freeze > requirements.txt`)*

### 4. Configuration

You will need to set up a few configuration files. **These files contain sensitive information and should NOT be committed to GitHub.** The project's `.gitignore` file is already set up to ignore them.

**a) Google Calendar API Credentials**

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  Enable the "Google Calendar API" for your project.
3.  Create credentials for a "Desktop app".
4.  Download the credentials JSON file and rename it to `credentials.json` in the root of your project directory.
5.  The first time you run the application, it will open a browser window asking you to authorize access to your calendar. After you approve, a `token.json` file will be created.

**b) OpenAI API Key**

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file and paste your OpenAI API key:
    ```
    OPENAI_API_KEY="your_secret_api_key_here"
    ```

**c) Your Personal Profile**

1.  Copy the example user profile file:
    ```bash
    cp user_profile.json.example user_profile.json
    ```
2.  Open `user_profile.json` and fill it in with your personal information, such as your timezone, priorities, and typical work hours.

### 5. Run the Application

Once everything is configured, start the Flask server:

```bash
python app.py
```

The application will be running at `http://127.0.0.1:5000`. Open this URL in your web browser.

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
