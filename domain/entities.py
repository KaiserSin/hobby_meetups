from dataclasses import dataclass

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
