import secrets

from files.helpers.config.const import *
from files.helpers.settings import get_setting
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app, limiter

def session_init():
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)

@app.before_request
def before_request():
	g.nonce = None

	if request.host != SITE:
		abort(403, "Unauthorized host provided!")

	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	if request.headers.get("CF-Worker"):
		abort(403, "Cloudflare workers are not allowed to access this website.")

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path != '/kofi':
		abort(403, 'Please use a "User-Agent" header!')

	if not get_setting('bots') and request.headers.get("Authorization"):
		abort(403)

	g.desires_auth = False
	if not IS_LOCALHOST:
		app.config["COOKIE_DOMAIN"] = f".{request.host}"
		app.config["SESSION_COOKIE_DOMAIN"] = app.config["COOKIE_DOMAIN"]

	ua = g.agent.lower()

	if '; wv) ' in ua:
		g.browser = 'webview'
	elif ' firefox/' in ua:
		g.browser = 'firefox'
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua:
		g.browser = 'apple'
	else:
		g.browser = 'chromium'

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

	"default-src": "'none'",
	"frame-ancestors": "'none'",

	"form-action": "'self'",
	"manifest-src": "'self'",
	"worker-src": "'self'",
	"base-uri": "'self'",
	"font-src": "'self'",
	"media-src": "'self'",

	"style-src-elem": "'self' 'nonce-{nonce}'",
	"style-src-attr": "'unsafe-inline'",
	"style-src": "'self' 'unsafe-inline'",

	"script-src-elem": "'self' 'nonce-{nonce}' challenges.cloudflare.com",
	"script-src-attr": "'unsafe-inline'",
	"script-src": "'self' 'unsafe-inline' challenges.cloudflare.com",

	"img-src": "https: data:",
	"frame-src": "challenges.cloudflare.com www.youtube-nocookie.com platform.twitter.com",
	"connect-src": "'self' tls-use1.fpapi.io api.fpjs.io",

	"report-to": "csp",
	"report-uri": "/csp_violations",
}

if IS_LOCALHOST:
	CSP["style-src-elem"] += " rdrama.net"
	CSP["script-src-elem"] += " rdrama.net"
	CSP["img-src"] += " http:"

CSP_str = ''

for k, val in CSP.items():
	CSP_str += f'{k} {val}; '

@app.after_request
def after_request(response:Response):
	if response.status_code < 400:
		_set_cloudflare_cookie(response)
		_commit_and_close_db()
	
	if g.nonce:
		response.headers.add("Report-To", {"group":"csp","max_age":10886400,"endpoints":[{"url":"/csp_violations"}]})
		response.headers.add("Content-Security-Policy", CSP_str.format(nonce=g.nonce))
	
	return response


@app.teardown_appcontext
def teardown_request(error):
	_rollback_and_close_db()
	stdout.flush()

def _set_cloudflare_cookie(response:Response) -> None:
	'''
	Sets a cookie that can be used by an upstream DDoS protection and caching provider
	'''
	if not g.desires_auth: return
	if not CLOUDFLARE_AVAILABLE or not CLOUDFLARE_COOKIE_VALUE: return
	logged_in = bool(getattr(g, 'v', None))
	if not logged_in and request.cookies.get("lo"):
		response.delete_cookie("lo", domain=app.config["COOKIE_DOMAIN"], samesite="Lax")
	elif logged_in and not request.cookies.get("lo"):
		response.set_cookie("lo", CLOUDFLARE_COOKIE_VALUE if logged_in else '', 
							max_age=SESSION_LIFETIME, samesite="Lax",
							domain=app.config["COOKIE_DOMAIN"])

def _commit_and_close_db() -> bool:
	if not getattr(g, 'db', None): return False
	g.db.commit()
	g.db.close()
	del g.db
	return True

def _rollback_and_close_db() -> bool:
	if not getattr(g, 'db', None): return False
	g.db.rollback()
	g.db.close()
	del g.db
	return True
