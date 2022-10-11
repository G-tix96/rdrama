from files.helpers.wrappers import *
from flask import *
from werkzeug.exceptions import HTTPException
from urllib.parse import quote, urlencode
import time
from files.__main__ import app, limiter

WERKZEUG_ERROR_DESCRIPTIONS = {
	400: "The browser (or proxy) sent a request that this server could not understand.",
	401: "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.",
	403: "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.",
	404: "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
	405: "The method is not allowed for the requested URL.",
	406: "The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
	413: "The data value transmitted exceeds the capacity limit.",
	414: "The length of the requested URL exceeds the capacity limit for  this server. The request cannot be processed.",
	415: "The server does not support the media type transmitted in the request.",
	418: "This server is a teapot, not a coffee machine",
	429: "This user has exceeded an allotted request count. Try again later.",
	500: "The server encountered an internal error and was unable to  complete your request. Either the server is overloaded or there is an error in the application.",
}

ERROR_TITLES = {
	400: "Bad Request",
	401: "Unauthorized",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	406: "Too Many Pings",
	413: "Max image/audio size is 8 MB (16 MB for paypigs)",
	414: "Max video size is 32 MB (64 MB for paypigs)",
	415: "Unsupported Media Type",
	417: "Image already exists!",
	418: "WEBM videos are not allowed",
	429: "Too Many Requests",
	500: "Internal Server Error",
}

ERROR_MSGS = {
	400: "That request was bad and you should feel bad.",
	401: "What you're trying to do requires an account. I think. The original error message said something about a castle and I hated that.",
	403: "YOU AREN'T WELCOME HERE GO AWAY",
	404: "Someone typed something wrong and it was probably you, please do better.",
	405: "idk how anyone gets this error but if you see this, remember to follow @carpathianflorist<BR>the original error text here talked about internet gremlins and wtf",
	406: "Max limit is 5 for comments and 50 for posts",
	413: "Max image/audio size is 8 MB (16 MB for paypigs)",
	414: "Max video size is 32 MB (64 MB for paypigs)",
	415: "Please upload only Image, Video, or Audio files!",
	417: "Image already exists!",
	418: "Please convert your video to MP4 and re-upload it!",
	429: "go spam somewhere else nerd",
	500: "Hiiiii it's carp! I think this error means that there's a timeout error. And I think that means something took too long to load so it decided not to work at all. If you keep seeing this on the same page <I>but not other pages</I>, then something is probably wrong with that specific function. It may not be called a function, but that sounds right to me. Anyway, ping me and I'll whine to someone smarter to fix it. Don't bother them. Thanks ily &lt;3",
}

ERROR_MARSEYS = {
	400: "marseybrainlet",
	401: "marseydead",
	403: "marseytroll",
	404: "marseyconfused",
	405: "marseyretard",
	406: "marseyrage",
	413: "marseyretard",
	414: "marseychonker2",
	415: "marseydetective",
	418: "marseytea",
	429: "marseyrentfree",
	500: "marseycarp3",
}

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
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
		return {"error": title, "code": e.code, "description": msg, "details": details}
	img = ERROR_MARSEYS.get(e.code, 'marseyl')
	return render_template('errors/error.html', err=True, title=title, msg=msg, details=details, img=img), e.code

@app.errorhandler(401)
def error_401(e):
	if request.headers.get("Authorization") or request.headers.get("xhr"): return {"error": "401 Unauthorized"}, 401
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
	if request.headers.get("Authorization") or request.headers.get("xhr"): return {"error": "500 Internal Server Error"}, 500
	else: return render_template('errors/500.html', err=True), 500


@app.post("/allow_nsfw")
def allow_nsfw():
	session["over_18"] = int(time.time()) + 3600
	redir = request.values.get("redir")
	if is_site_url(redir): return redirect(redir)
	return redirect('/')
