from files.__main__ import app
from files.events import EVENT_JINJA_CONST

@app.context_processor
def event_constants():
	return EVENT_JINJA_CONST
