from typing import Union
from sqlalchemy.orm import scoped_session

from files.events.classes.eventuser import EventUser
from files.classes.user import User

def get_or_create_event_user(target:Union[int, User], db:scoped_session) -> EventUser:
	if isinstance(target, User): target = target.id  # type: ignore
	user = db.get(EventUser, target)
	if not user:
		user = EventUser(id=target)
		db.add(target)
		db.flush()
	return user
