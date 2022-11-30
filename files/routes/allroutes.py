import secrets

from files.helpers.const import *
from files.helpers.settings import get_setting
from files.helpers.security import generate_hash
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app, limiter

def session_init():
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)

@app.before_request
def before_request():
	g.desires_auth = False
	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path != '/kofi':
		return 'Please use a "User-Agent" header!', 403

	ua = g.agent.lower()

	if request.host != SITE:
		return {"error": "Unauthorized host provided"}, 403

	if request.headers.get("CF-Worker"): return {"error": "Cloudflare workers are not allowed to access this website."}, 403

	if not get_setting('Bots') and request.headers.get("Authorization"): abort(403)

	g.nonce = generate_hash(f'{time.time()}+{session.get("session_id")}')

	g.webview = '; wv) ' in ua

	if ' firefox/' in ua:
		g.type = 'firefox'
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua:
		g.type = 'apple'
	else:
		g.type = 'chromium'

	g.is_tor = request.headers.get("cf-ipcountry") == "T1"

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

	session_init()
	limiter.check()
	g.db = db_session()


CSP = {
	"upgrade-insecure-requests": "",
	"object-src": "'none'",
	"form-action": "'self'",
	"manifest-src": "'self'",
	"worker-src": "'self'",
	"base-uri": "'self'",
	"style-src-elem": "'self' 'nonce-{nonce}'",
	"script-src-elem": "'self' 'nonce-{nonce}' challenges.cloudflare.com rdrama.net",
	"script-src": "'self' 'unsafe-inline' challenges.cloudflare.com rdrama.net",
	"frame-src": "challenges.cloudflare.com www.youtube-nocookie.com platform.twitter.com",
	"connect-src": "'self' tls-use1.fpapi.io api.fpjs.io 00bb6d59-7b11-4339-b1ae-b1f1259d1316.pushnotifications.pusher.com",
	"report-to": "csp",
	"report-uri": "/sex",
}

if not IS_LOCALHOST:
	CSP["default-src"] = "https:"
	CSP["img-src"] = "https: data:"

CSP_str = ''

for k, val in CSP.items():
	CSP_str += f'{k} {val}; '

@app.after_request
def after_request(response):
	if response.status_code < 400:
		if CLOUDFLARE_AVAILABLE and CLOUDFLARE_COOKIE_VALUE and g.desires_auth:
			logged_in = bool(getattr(g, 'v', None))
			response.set_cookie("lo", CLOUDFLARE_COOKIE_VALUE if logged_in else '', 
								max_age=60*60*24*365 if logged_in else 1, samesite="Lax")
		if getattr(g, 'db', None):
			g.db.commit()
			g.db.close()
			del g.db

	response.headers.add("Report-To", {"group":"csp","max_age":10886400,"endpoints":[{"url":"/sex"}]})
	response.headers.add("Content-Security-Policy", CSP_str.format(nonce=g.nonce))

	return response


@app.teardown_appcontext
def teardown_request(error):
	if getattr(g, 'db', None):
		g.db.rollback()
		g.db.close()
		del g.db
	stdout.flush()
