import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime 
from googleapiclient.errors import HttpError
from typing import Any, Optional
from zoneinfo import ZoneInfo
import secrets


SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self, token_path = 'token.json', creds_path='credentials.json'):
        self.token_path = token_path
        self.creds_path = creds_path
        self.creds = None
        self.service = None

        # Try to load existing credentials, but don't crash if they don't exist
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if self.creds and self.creds.valid:
                self.service = build('calendar', 'v3', credentials=self.creds)
                print('Google Calendar Service successfully initialized.')
            elif self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    with open(token_path, 'w') as token:
                        token.write(self.creds.to_json())
                    self.service = build('calendar', 'v3', credentials=self.creds)
                    print('Credentials refreshed. Google Calendar Service successfully initialized.')
                except Exception as e:
                    print(f'Failed to refresh credentials: {e}')
                    self.creds = None
                    self.service = None
            else:
                print('Token exists but is invalid and cannot be refreshed.')
                self.creds = None
        else:
            print('No token.json found. User needs to authenticate via /google/login.')

    def is_authenticated(self) -> bool:
        """Check if the service has valid credentials."""
        return self.service is not None

    def authenticate_new_user(self, port: int = None) -> bool:
        """Run the OAuth flow for a new user using local server."""
        if not os.path.exists(self.creds_path):
            raise Exception(f"Credentials file not found at {self.creds_path}")
        
        try:
            # Use a random port if not specified
            if port is None:
                port = 8080 + secrets.randbelow(1000)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.creds_path,
                scopes=SCOPES
            )
            
            # Run local server to handle OAuth callback
            self.creds = flow.run_local_server(
                port=port,
                authorization_prompt_message='Please visit this URL to authorize the application: {url}',
                success_message='Authentication successful! You can close this window.',
                open_browser=True
            )
            
            # Save the credentials
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
            
            # Initialize the service
            self.service = build('calendar', 'v3', credentials=self.creds)
            print('Authentication successful! Token saved and Google Calendar Service initialized.')
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def _ensure_valid_credentials(self):
        """Ensure credentials are valid before making API calls."""
        if not self.creds:
            raise Exception("Not authenticated. Please log in via /google/login")
        
        if self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())
                print('Credentials refreshed automatically.')
            except Exception as e:
                raise Exception(f"Failed to refresh credentials: {e}")
        
        if not self.service:
            self.service = build('calendar', 'v3', credentials=self.creds)


    def insert_event(self, event_body: dict[str, Any]):
        """
        Inserts an event into the primary calendar using a pre-validated dictionary.
        """
        self._ensure_valid_credentials()

        try: 
            if 'start' in event_body and 'dateTime' in event_body['start']:
                event_body['start']['dateTime'] = event_body['start']['dateTime'].isoformat()
        
            if 'end' in event_body and 'dateTime' in event_body['end']:
                event_body['end']['dateTime'] = event_body['end']['dateTime'].isoformat()
            
            created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()

            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise 

    def search_events(self, query: str, max_results: int = 5):
        """
        Searches for events in the primary calendar matching the given query string.
        """
        self._ensure_valid_credentials()
        
        try:
            # Get the ZoneInfo object for Central European Time
            cet_tz = ZoneInfo("Europe/Berlin")
            now = datetime.datetime.now(cet_tz).isoformat()
            events_result = self.service.events().list(
                calendarId='primary', 
                q=query,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            print(f"Found {len(events)} events matching query '{query}'.")
            return events
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def delete_event(self, event_id: str):
        """
        Deletes an event in the primary calendar matching the given event id.
        """
        self._ensure_valid_credentials()
        
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(F"Event deleted: {event_id}")
            return 
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def update_event(self, event_id: str, updated_data: dict[str, Any]):
        """
        Updates an event if the primary calendar matching the given event id.
        """
        self._ensure_valid_credentials()
        
        try:
            event_updates = self.service.events().update(
                calendarId ='primary', 
                eventId = event_id, 
                body= updated_data
            ).execute()

            print(f"Event updated: {event_updates.get('htmlLink')}")
            return event_updates
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    




