import cli_ui as cli
import validators
import urllib.request
import datetime

from bs4 import BeautifulSoup
from src.google_api import *
from src.settings import *

os.environ["ROOT_DIR"] = os.path.dirname(os.path.realpath(__file__))

# =========================================================================dd==
#   AUTHENTICATE USER'S GOOGLE ACCOUNT
# =========================================================================dd==

# Initialize API
api = GoogleAPI()
# Authenticate user
api.authenticate()

# Initialize app settings
settings = Settings(api)
# Get settings (load/ask)
settings.load_or_ask()

repeat = True
while repeat:
    repeat = False

    # Make user select
    course_url = ""
    while True:
        course_url = cli.ask_string("Provide course URL:")
        if course_url:
            course_url = course_url.strip()
            if validators.url(course_url):
                break

        print("Provided URL is not valid, please try again.")

    events = []
    day_offsets = {
        "Po": 0,
        "Mon": 0,
        "Út": 1,
        "Tue": 1,
        "St": 2,
        "Wed": 2,
        "Čt": 3,
        "Thu": 3,
        "Pá": 4,
        "Fri": 4,
    }

    print("Loading course webpage...")
    contents = urllib.request.urlopen(course_url).read()

    print("Parsing course webpage...")
    webpage = BeautifulSoup(contents, 'lxml')
    content_table = webpage.find("table", {"class": "tcur"})

    course_data = content_table.find_all_next("td")
    course_name = course_data[0].text
    course_abbr = course_data[1].text

    schedule_table = content_table.find_all("table", {"border": 1, "bordercolor": "#888888"})[1]
    schedule_entries = schedule_table.find_all("tr")
    for schedule_entry in schedule_entries:
        cols = schedule_entry.find_all("td")
        if not len(cols):
            continue

        events.append({
            "day": schedule_entry.th.text,
            "time_from": cols[3].text.strip(),
            "time_to": cols[4].text.strip(),
            "rooms": cols[2].text.strip().split(' '),
            "is_exercise": cols[0].text.strip() != "přednáška" and cols[0].text.strip() != "lecture",
        })

    print("Importing course events...")
    for e in events:
        room = e['rooms'][0]
        for r in ["D105", "E112"]:
            if r in e['rooms']:
                room = r

        time_from = e['time_from'].split(':')
        course_date_from = settings.date_from + datetime.timedelta(
            days=day_offsets[e['day']],
            hours=int(time_from[0]),
            minutes=int(time_from[1]),
        )

        time_to = e['time_to'].split(':')
        course_date_to = settings.date_from + datetime.timedelta(
            days=day_offsets[e['day']],
            hours=int(time_to[0]),
            minutes=int(time_to[1]),
        )

        colorId = settings.lecture_color['id']
        if e['is_exercise']:
            colorId = settings.exercise_color['id']

        event = {
            'summary': f"[{course_abbr}] {course_name}",
            'location': room,
            'description': '',
            'colorId': colorId,
            'source': {
                'title': "FIT VUTBR - " + course_name,
                'url': course_url,
            },
            'start': {
                'dateTime': course_date_from.isoformat(),
                'timeZone': 'Europe/Prague',
            },
            'end': {
                'dateTime': course_date_to.isoformat(),
                'timeZone': 'Europe/Prague',
            },
            'recurrence': [
                'RRULE:FREQ=WEEKLY;COUNT=13'
            ],
        }

        api_event = api.calendar_service().events().insert(calendarId=settings.calendar['id'], body=event).execute()
        print(f"Created event {api_event['htmlLink']}")

    repeat = cli.ask_yes_no("Continue with more courses?", default=True)
