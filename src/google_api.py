import pickle
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleAPI:

    creds = None

    service_calendar = None

    def authenticate(self):
        token_path = os.getenv("ROOT_DIR") + '/conf/token.pickle'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        credentials_path = os.getenv("ROOT_DIR") + '/conf/credentials.json'
        if not os.path.exists(credentials_path):
            print("Google API credentials not found, please visit https://developers.google.com/calendar/quickstart/python and follow 'Step 1'. Save the 'credentials.json' to 'conf' folder.")
            exit(1)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

    def calendar_service(self):
        if self.service_calendar is None:
            self.service_calendar = build('calendar', 'v3', credentials=self.creds)

        return self.service_calendar

    def get_calendar_list(self):
        return self.calendar_service().calendarList().list().execute()

    def get_color_list(self):
        return self.calendar_service().colors().get().execute()

    def get_calendar(self, calendar_id="primary"):
        return self.calendar_service().calendars().get(calendarId=calendar_id).execute()

    def create_event(self, calendar_id, event):
        return self.calendar_service().events().insert(calendarId=calendar_id, body=event).execute()
