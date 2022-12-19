from sqlalchemy import inspect

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED, AWARDS_DISABLED
from files.__main__ import engine

from files.events.classes import *
from files.events.helpers import *
from files.events.routes import *

def _build_table():
	if not inspect(engine).has_table(EventUser.__table__.name, schema="public"):
		print("[EVENT] Building event table...")
		EventUser.__table__.create(bind=engine, checkfirst=True)

def _populate_awards():
	temp = {x: AWARDS_ENABLED[x] for x in AWARDS_ENABLED if x not in EVENT_AWARDS}
	AWARDS_ENABLED.clear()
	AWARDS_ENABLED.update(EVENT_AWARDS)
	AWARDS_ENABLED.update(temp)

	for award in EVENT_AWARDS:
		EVENT_AWARDS[award]['ghost'] = EVENT_AWARDS[award]['cosmetic']
		if award in AWARDS_DISABLED:
			AWARDS_DISABLED.remove(award)

	AWARDS.update(EVENT_AWARDS)

def event_init():
	_build_table()

_populate_awards()
