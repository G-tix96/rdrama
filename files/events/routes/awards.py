from flask import g

from files.events.helpers.get import get_or_create_event_user

def award_thing_event(v, kind, author):
	event_author = get_or_create_event_user(author, g.db)
	event_v = get_or_create_event_user(v, g.db)

	g.db.add(event_author)
