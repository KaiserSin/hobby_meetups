from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    password_hash: str

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Meetup:
    id: int
    user_id: int
    title: str
    description: str
    event_time: str
    location: str
    category_name: str = None
    username: str = None
    category_ids: tuple = ()

    @property
    def event_time_label(self):
        return _format_datetime(self.event_time, "%Y-%m-%d %H:%M")

    @property
    def event_time_for_input(self):
        return _format_datetime(self.event_time, "%Y-%m-%dT%H:%M")

def _format_datetime(value, output_format):
    parsed_datetime = _parse_datetime(value)
    if parsed_datetime is None:
        return value
    return parsed_datetime.strftime(output_format)

def _parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None
