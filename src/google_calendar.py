import asyncio
import json
from datetime import datetime, timedelta
from pprint import pprint
from typing import List, Tuple

from requests import HTTPError
from base import BaseClass
from googleapiclient.discovery import build
from google.oauth2 import service_account

from config import config
from custom_types import Event
from constants import DATE_FORMAT
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
        try:
            return service_account.Credentials.from_service_account_file(
                config.calendar_credentials_file, scopes=config.calendar_scopes
            )
        except Exception as e:
            self.log("Error get_credentials: %s" % e)
            raise e

    def get_events(self, start_time: str = None, max_results: int = 10) -> List[Event]:
        all_events: List[Tuple[datetime, str]] = []

        try:
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            # format start_time to isoformat
            formattedStartTime = (
                str(datetime.strptime(start_time, "%Y-%m-%d").strftime(DATE_FORMAT))
                if start_time
                else None
            )
            self.log(formattedStartTime)
            timeMin = formattedStartTime if formattedStartTime else now
            self.log(f"timeMin = {timeMin}")
            self.log(f"Getting the upcoming {max_results} events from {timeMin}...")
            options = {
                "timeMin": timeMin,
                "maxResults": max_results,
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
                "Error: GoogleCalendar received %s while retrieving events"
                % e.resp.status
            )
        finally:
            self.log("Got %s events" % len(all_events))
            return all_events

    def formart_date(self, date: datetime) -> str:
        return date.isoformat() + "Z"

    async def create_event(self, event: Event) -> Event:
        event = (
            self.service.events()
            .insert(calendarId=config.calendar_id, body=event)
            .execute()
        )
        self.log("Event created: %s" % (event.get("htmlLink")))
        return event

    async def delete_event(self, event_id) -> str:
        self.service.events().delete(
            calendarId=config.calendar_id, eventId=event_id
        ).execute()
        self.log("Event deleted: %s" % (event_id))
        return event_id

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

    def build_events(self, topical_problems: List[List[str]]) -> List[Event]:
        events = []
        dates = self.set_event_dates()

        seen = set()
        for date, count in dates:
            for topic, problems in topical_problems.items():
                for problem in problems:
                    # ensure only two events are scheduled on the same day and that the event is not already scheduled
                    if count >= self.daily_question_limit or (
                        problem["problem"].lower() in seen
                    ):
                        continue

                    # if same day startTime should be 1 hour after endTime of previous event if any
                    if count > 0:
                        startTime = (
                            datetime.strptime(
                                events[-1]["end"]["dateTime"], DATE_FORMAT
                            )
                            + timedelta(
                                hours=self.get_time_limit_for_problem(
                                    self.get_difficulty_from_color(
                                        events[-1]["colorId"]
                                    )
                                )
                            )
                            if len(events) > 0
                            else datetime.strptime(date, DATE_FORMAT)
                        )
                    else:
                        startTime = datetime.strptime(date, DATE_FORMAT)

                    endTime = startTime + timedelta(
                        hours=self.get_time_limit_for_problem(problem["difficulty"])
                    )

                    event = self.create_event_object(topic, problem, startTime, endTime)

                    seen.add(problem["problem"].lower())
                    count += 1

                    events.append(event)

        events.sort(key=lambda event: event["start"]["dateTime"])
        self.log("Sorted %s events" % len(events))
        return events[: self.total_question_limit]

    def get_color_for_problem(self, problem) -> int:
        difficulty_color_map = {
            "Easy": 1,  # blue
            "Medium": 2,  # green
            "Hard": 3,  # red
        }

        return difficulty_color_map.get(problem["difficulty"], "Easy")

    def get_difficulty_from_color(self, color) -> str:
        difficulty_color_map = {
            1: "Easy",
            2: "Medium",
            3: "Hard",
        }

        return difficulty_color_map.get(color, "Easy")

    def get_time_limit_for_problem(self, difficulty: str) -> int:
        difficulty_time_limit_map = {
            "Easy": 0.5,  # 30 mins
            "Medium": 0.75,  # 45 min
            "Hard": 0.75,  # 45 min
        }

        return difficulty_time_limit_map.get(difficulty, 0.5)

    def set_event_dates(self) -> List[Tuple[datetime, int]]:
        return list(
            map(
                lambda i: (
                    self.formart_date(datetime.now() + timedelta(days=i)),
                    0,
                ),
                range(self.total_question_limit),
            )
        )

    def create_event_object(self, topic, problem, startTime, endTime) -> Event:
        return {
            "summary": f"{topic} - {problem['problem']} ({problem['difficulty']})",
            "description": problem["link"],
            "start": {
                "dateTime": self.formart_date(startTime),
                "timeZone": config.timezone,
            },
            "end": {
                "dateTime": self.formart_date(endTime),
                "timeZone": config.timezone,
            },
            "colorId": self.get_color_for_problem(problem),
        }

    async def create_problem_schedule(self) -> List[Event]:
        topical_problems = self.load_problems()
        events = self.build_events(topical_problems)
        self.log("Creating %s events" % len(events))
        if self.dry:
            self.log("Dry run, not creating events")
            return
        try:
            tasks = [self.create_event(event) for event in events]
            # tasks executed concurrently using asyncio.gather
            results = await asyncio.gather(*tasks)
            self.log("Created %s events" % len(results))
        except HTTPError as e:
            self.log(
                "Error: GoogleCalendar received %s while creating events"
                % e.resp.status
            )
        finally:
            return events

    def get_event_ids_from_calendar(self) -> List[str]:
        next_page_token = None
        event_ids = []
        try:
            while True:
                options = {
                    "calendarId": config.calendar_id,
                    "maxResults": 500,  # Adjust as needed
                    "pageToken": next_page_token,
                }

                response = self.service.events().list(**options).execute()
                events = response.get("items", [])

                self.log("Got %s events from token %s" % (len(events), next_page_token))

                next_page_token = response.get("nextPageToken", None)

                if not next_page_token:
                    # No more pages, exit the loop
                    break

                if events:
                    for event in events:
                        event_ids.append(event["id"])
                self.log("Got %s event ids" % len(event_ids))

            return event_ids
        except HTTPError as e:
            self.log(
                "Error: GoogleCalendar received %s while retrieving events"
                % e.resp.status
            )
            raise e

    async def delete_all_events(self, event_ids) -> int:
        count = 0

        if self.dry:
            self.log("Dry run, not deleting events :)")
            return count

        try:
            tasks = [self.delete_event(id) for id in event_ids]

            results = await asyncio.gather(*tasks) if len(tasks) > 0 else []
            count = len(results)
        except HTTPError as e:
            self.log(
                "Error: GoogleCalendar received %s while retrieving events"
                % e.resp.status
            )
        finally:
            self.log("Deleted %s events" % count)
            return count
