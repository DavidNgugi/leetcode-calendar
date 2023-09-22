import click
import os
from dotenv import load_dotenv
from pprint import pformat
from typing import List

from utils.utils import get_file_path

load_dotenv()

class Config:

    def __init__(self) -> None:
        self.base_url = os.getenv("BASE_URL", "https://neetcode.io/practice")
        self.log_level = os.getenv("LOG_LEVEL", "DEBUG")
        self.calendar_credentials_file = get_file_path(os.getenv("CALENDAR_CREDENTIALS_FILE", "credentials.json"))
        self.calendar_scopes = self.get_scope_list(os.getenv("CALENDAR_SCOPES", 'https://www.googleapis.com/auth/calendar'))
        self.calendar_id = os.getenv("CALENDAR_ID", "primary")
        self.problems_file = os.getenv("PROBLEMS_FILE", "problems.json")
        self.daily_question_limit = int(os.getenv("DAILY_QUESTION_LIMIT", 2))
        self.total_question_limit = int(os.getenv("TOTAL_QUESTION_LIMIT", 10))
        self.question_time_limit = float(os.getenv("QUESTION_TIME_LIMIT", 1))
        self.timezone = os.getenv("TIMEZONE", "America/Los_Angeles")
    
    def get_scope_list(self, scopes: str) -> List[str]:
        return scopes.split(",")
    
config = Config()

########### Command-line script ###########
@click.command()
@click.argument("key", required=False)
def list_vars(key=None):
    """List configuration values for the Skill-Assessments project"""
    if key:
        print("{}={}".format(key, pformat(getattr(config, key))))
    else:
        for var, value in sorted(config.__dict__.items()):
            if not var.startswith("__"):
                print("{}={}".format(var, pformat(value)))


if __name__ == "__main__":
    list_vars()