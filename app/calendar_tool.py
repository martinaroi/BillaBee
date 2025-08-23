from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/home/maroithmeier/BillaBee/app/credentials.json', SCOPES)
            print(f"Using redirect URI: http://localhost:{42409}/")
            creds = flow.run_local_server(port=42409)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Test Event from Python',
        'location': 'Online', 
        'description': 'Just testing the Gooogle Calendar API', 
        'start': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=35)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
    }

    event = service.events().insert(calendarId = 'primary', body = event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    main()
