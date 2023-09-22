import json
import datetime
from pprint import pprint
from typing import List, Tuple

from requests import HTTPError
from base import BaseClass
from googleapiclient.discovery import build
from google.oauth2 import service_account

from config import config
from custom_types import Event
from utils.utils import get_file_path


class GoogleCalendar(BaseClass):
    def __init__(self, dry: bool = False, verbose: bool = False) -> None:
        super().__init__(dry, verbose)
        self.service = build("calendar", "v3", credentials=self.get_credentials())
        self.daily_question_limit = config.daily_question_limit
        self.total_question_limit = config.total_question_limit

    def __str__(self):
        return "Calendar(dry={}, verbose={})".format(self.dry, self.verbose)

    def get_credentials(self):
        return service_account.Credentials.from_service_account_file(
            config.calendar_credentials_file, scopes=config.calendar_scopes
        )

    def get_events(self) -> List[Event]:
        # Call the Calendar API
        all_events: List[Tuple[datetime.datetime, str]] = []

        try:
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            self.log("Getting the upcoming 10 events from now %s" % now)
            options = {
                "timeMin": now,
                "maxResults": 10,
                "singleEvents": True,
                "orderBy": "startTime",
            }
            events_result = (
                self.service.events()
                .list(calendarId=config.calendar_id, **options)
                .execute()
            )

            events = events_result.get("items", [])

            if not events:
                self.log("No upcoming events found.")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    all_events.append((start, event["summary"]))
        except HTTPError as e:
            self.log(
                "GoogleCalendar received %s while retrieving events" % e.resp.status
            )
        finally:
            self.log("Got %s events" % len(all_events))
            return all_events

    def formart_date(self, date: datetime.datetime) -> str:
        return date.isoformat() + "Z"

    def create_event(self, event: Event):
        event = (
            self.service.events()
            .insert(calendarId=config.calendar_id, body=event)
            .execute()
        )
        self.log("Event created: %s" % (event.get("htmlLink")))
        return event

    def delete_event(self, event_id):
        self.service.events().delete(
            calendarId=config.calendar_id, eventId=event_id
        ).execute()
        self.log("Event deleted: %s" % (event_id))

    def load_problems(
        self,
    ) -> List[List[str]]:
        try:
            path_to_file = get_file_path(config.problems_file)
            self.log("Loading problems from %s" % config.problems_file)
            with open(path_to_file, "r") as json_file:
                data = json.load(json_file)
                self.log("Loaded %s topics" % len(data))
            return data
        except Exception as e:
            self.log("Error: %s" % e)
            return []

    def build_events(self, topical_problems: List[List[str]]):
        events = []
        # 2 problems(events) per day
        dates = list(
            map(
                lambda i: (
                    self.formart_date(
                        datetime.datetime.now() + datetime.timedelta(days=i)
                    ),
                    0,
                ),
                range(self.total_question_limit),
            )
        )

        # loop through dates and topics and create events
        seen = set()
        for date, count in dates:
            for topic, problems in topical_problems.items():
                # self.log("Creating event for %s" % topic)
                for problem in problems:
                    # ensure only two events are scheduled on the same day and that the event is not already scheduled
                    if count >= self.daily_question_limit or (
                        problem["problem"].lower() in seen
                    ):
                        continue

                    # if same day startTime should be 1 hour after endTime of previous event if any
                    if count > 0:
                        startTime = (
                            datetime.datetime.strptime(
                                events[-1]["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                            + datetime.timedelta(hours=1)
                            if len(events) > 0
                            else datetime.datetime.strptime(
                                date, "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                        )
                    else:
                        startTime = datetime.datetime.strptime(
                            date, "%Y-%m-%dT%H:%M:%S.%fZ"
                        )

                    endTime = startTime + datetime.timedelta(hours=config.question_time_limit)

                    event = {
                        "summary": f"{topic} - {problem['problem']} ({problem['difficulty']})",
                        "description": problem["link"],
                        "start": {
                            "dateTime": self.formart_date(startTime),
                            "timeZone": "Asia/Kolkata",
                        },
                        "end": {
                            "dateTime": self.formart_date(endTime),
                            "timeZone": "Asia/Kolkata",
                        },
                    }

                    seen.add(problem["problem"].lower())
                    count += 1

                    events.append(event)

        # sort events by date
        events.sort(key=lambda event: event["start"]["dateTime"])
        self.log("Sorted %s events" % len(events))
        return events[:self.total_question_limit]

    async def create_problem_schedule(self):
        topical_problems = self.load_problems()
        events = self.build_events(topical_problems)
        self.log("Creating %s events" % len(events))
        if self.dry:
            self.log("Dry run, not creating events")
            return
        for event in events:
            self.create_event(event)
        self.log("Created %s events" % len(events))

    def delete_all_events(self):
        eventsObj = self.service.events().list(calendarId=config.calendar_id).execute()
        if self.dry:
            self.log("Dry run, not deleting events")
            return
        events = eventsObj.get("items", [])
        for event in events:
            self.delete_event(event["id"])
        self.log("Deleted %s events" % len(events))
