
from typing import Generic, TypeVar

TEvent = TypeVar("TEvent", bound=dict[str, str])
# Event = Generic[TEvent]
# {
#     'summary': 'Test event',
#     'location': '800 Howard St., San Francisco, CA 94103',
#     'description': 'A chance to hear more about Google\'s developer products.',
#     'start': {
#         'dateTime': '2023-10-21T09:00:00-07:00',
#         'timeZone': 'America/Los_Angeles',
#     },
#     'end': {
#         'dateTime': '2023-10-21T10:00:00-08:00',
#         'timeZone': 'America/Los_Angeles',
#     },
#     'recurrence': [
#         # dont repeat
#         'RRULE:FREQ=DAILY;COUNT=1'
#     ],
#     'attendees': [
#        {'email': ''},
#     ],
#     'colorId': 1,
# }
class Event(Generic[TEvent]):
    def __init__(self) -> None:
        self.summary: str = ""
        self.location: str = ""
        self.description: str = ""
        self.start: dict[str, str] = {}
        self.end: dict[str, str] = {}
        self.recurrence: list[str] = []
        self.colorId: int = 0

    def __str__(self) -> str:
        return "Event(summary={}, location={}, description={}, start={}, end={}, recurrence={}, colorId={})".format(
            self.summary, self.location, self.description, self.start, self.end, self.recurrence, self.colorId
        )
    
    def __repr__(self) -> str:
        return self.__str__()