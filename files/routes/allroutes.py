from files.helpers.const import *
from files.helpers.settings import get_setting
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app

@app.before_request
def before_request():
	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	g.agent = request.headers.get("User-Agent")
	if not g.agent and request.path != '/kofi':
		return 'Please use a "User-Agent" header!', 403

	ua = g.agent or ''
	ua = ua.lower()

	if request.host != SITE:
		return {"error": "Unauthorized host provided"}, 403

	if request.headers.get("CF-Worker"): return {"error": "Cloudflare workers are not allowed to access this website."}, 403

	if not get_setting('Bots') and request.headers.get("Authorization"): abort(403)

	g.db = db_session()

	if ' firefox/' in ua:
		g.type = 'firefox'
		g.inferior_browser = True
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua:
		g.type = 'apple'
		g.inferior_browser = True
	else:
		g.type = 'chromium'
		g.inferior_browser = False

	g.is_tor = request.headers.get("cf-ipcountry") == "T1"

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

@app.after_request
def after_request(response):
	if response.status_code < 400:
		if CLOUDFLARE_AVAILABLE and CLOUDFLARE_COOKIE_VALUE and getattr(g, 'desires_auth', False):
			logged_in = bool(getattr(g, 'v', None))
			response.set_cookie("lo", CLOUDFLARE_COOKIE_VALUE if logged_in else '', 
								max_age=60*60*24*365 if logged_in else 1, samesite="Lax")
		if getattr(g, 'db', None):
			g.db.commit()
			g.db.close()
			del g.db
	return response

@app.teardown_appcontext
def teardown_request(error):
	if getattr(g, 'db', None):
		g.db.rollback()
		g.db.close()
		del g.db
	stdout.flush()
