import cli_ui as cli

from src.google_api import *
from colored import fg, bg, attr, stylize


class Settings:
    api = None
    settings_path = None

    calendar = None
    lecture_color = None
    exercise_color = None

    def __init__(self, api: GoogleAPI):
        self.api = api
        self.settings_path = os.getenv("ROOT_DIR") + '/conf/settings.pickle'

    def load_or_ask(self):
        if self.exists():
            self.load()
            self.print()
            ask = cli.ask_yes_no("Would you like to provide new settings?")
            if not ask:
                return

        self.ask()

    def ask(self):
        # Get list of calendars
        calendars = self.api.get_calendar_list()['items']

        # Make user select calendar
        self.calendar = cli.ask_choice("Select calendar to sync:", choices=calendars,
                                       func_desc=lambda c: c['summary'])

        # Get list of colors
        colors = self.api.get_color_list()
        event_colors = []
        for color_id in colors['event']:
            color = colors['event'][color_id]
            color['id'] = color_id
            event_colors.append(color)

        self.lecture_color = cli.ask_choice("Select color for " + stylize("lecture", attr('bold')) + " events (2):",
                                            choices=event_colors,
                                            func_desc=lambda
                                                c: f"https://www.color-hex.com/color/{c['background'][1:]}")

        self.exercise_color = cli.ask_choice("Select color for " + stylize("exercise", attr('bold')) + " events (1):",
                                             choices=event_colors,
                                             func_desc=lambda
                                                 c: f"https://www.color-hex.com/color/{c['background'][1:]}")

        self.save()

    def print(self):
        print(f"Loaded saved settings!\n"
              f"Calendar:\t\t{self.calendar['summary']}\n"
              f"Lecture color:\t{self.lecture_color['background']}\n"
              f"Exercise color:\t{self.exercise_color['background']}")

    def exists(self):
        return os.path.exists(os.getenv("ROOT_DIR") + '/conf/settings.pickle')

    def load(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'rb') as settings:
                self.calendar, self.lecture_color, self.exercise_color = pickle.load(settings)

    def save(self):
        with open(self.settings_path, 'wb') as settings:
            pickle.dump((self.calendar, self.lecture_color, self.exercise_color), settings)
