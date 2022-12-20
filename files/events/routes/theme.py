from files.events.helpers import get_or_create_event_user
from files.__main__ import g, app
from files.routes.wrappers import auth_required

@app.post("/events/fistmas2022/darkmode")
@auth_required
def event_darkmode(v):
	user = get_or_create_event_user(v, g.db)
	if user.event_darkmode:
		user.event_darkmode = False
	else:
		user.event_darkmode = True

	g.db.add(user)

	return {"message": "Dark mode toggled successfully!"}
