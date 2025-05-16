from models import User
from typing import Optional, List

_users = []
_journals = {}  # key: username, value: journal data

def get_user_by_username(username: str) -> Optional[User]:
    for u in _users:
        if u.username == username:
            return u
    return None

def create_user(user: User):
    _users.append(user)

def get_all_users() -> List[User]:
    return list(_users)

def promote_user(username: str):
    u = get_user_by_username(username)
    if u:
        u.role = "therapist"

def get_journal_by_username(username: str):
    # Return the journal for the given username, or None if not found.
    return _journals.get(username)