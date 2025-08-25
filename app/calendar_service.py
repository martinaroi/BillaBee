import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import datetime 
from googleapiclient.errors import HttpError
from typing import Any
from zoneinfo import ZoneInfo


SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self, token_path = 'token.json', creds_path='credentials.json'):
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid: 
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print('Credentials refreshed.')
            else:
                raise Exception(f"Fatal Error: Could not load valid Google credentials from {token_path}. "
                                "Please run the one-time authentication script to generate a valid token.json file.")

        self.service = build('calendar', 'v3', credentials=creds)

        print('Google Calendar Service successfully initialized.')


    def insert_event(self, event_body: dict[str, Any]):
        """
        Inserts an event into the primary calendar using a pre-validated dictionary.
        """

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
    




