from calendar_service import GoogleCalendarService
import os


class AppContext:
    def __init__(self):
        """
        Initializes the application context by creating instances of all necessary services.
        Calendar service will initialize even without authentication - user can authenticate later via /google/login.
        """
        try: 
            self.calendar_service = GoogleCalendarService()
            print('Context initialized successfully.')
        except Exception as e:
            print(f"WARNING: Could not initialize Google Calendar service: {e}")
            self.calendar_service = None