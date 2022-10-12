from files.helpers.wrappers import *
from flask import *
from urllib.parse import quote, urlencode
import time
from files.__main__ import app, limiter

# If you're adding an error, go here:
# https://github.com/pallets/werkzeug/blob/main/src/werkzeug/exceptions.py
# and copy the description for the error code you're adding and add it to
# the constant WERKZEUG_ERROR_DESCRIPTIONS so that the default error message
# doesn't show up on the message. Be exact or it won't work properly.

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
@app.errorhandler(409)
@app.errorhandler(413)
@app.errorhandler(414)
@app.errorhandler(415)
@app.errorhandler(417)
@app.errorhandler(418)
@app.errorhandler(429)
def error(e):
	title = ERROR_TITLES.get(e.code, str(e.code))
	msg = ERROR_MSGS.get(e.code, str(e.code))
	details = e.description

	if WERKZEUG_ERROR_DESCRIPTIONS.get(e.code, None) == details:
		details = None
	if request.headers.get("Authorization") or request.headers.get("xhr"):
		return {"error": title, "code": e.code, "description": msg, "details": details}, e.code
	img = ERROR_MARSEYS.get(e.code, 'marseyl')
	return render_template('errors/error.html', err=True, title=title, msg=msg, details=details, img=img), e.code

@app.errorhandler(401)
def error_401(e):
	if request.headers.get("Authorization") or request.headers.get("xhr"): return error(e)
	else:
		path = request.path
		qs = urlencode(dict(request.values))
		argval = quote(f"{path}?{qs}", safe='').replace('/logged_out','')
		if not argval: argval = '/'
		if session.get("history"): return redirect(f"/login?redirect={argval}")
		else: return redirect(f"/signup?redirect={argval}")

@app.errorhandler(500)
def error_500(e):
	g.db.rollback()
	return error(e)


@app.post("/allow_nsfw")
def allow_nsfw():
	session["over_18"] = int(time.time()) + 3600
	redir = request.values.get("redir")
	if is_site_url(redir): return redirect(redir)
	return redirect('/')
