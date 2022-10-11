from .get import *
from .alerts import *
from files.helpers.const import *
from files.helpers.get import *
from files.__main__ import db_session, limiter
from random import randint
import functools
import user_agents
import time

def get_logged_in_user():

	if hasattr(g, 'v'): return g.v

	if not (hasattr(g, 'db') and g.db): g.db = db_session()

	v = None

	token = request.headers.get("Authorization","").strip()
	if token:
		client = g.db.query(ClientAuth).filter(ClientAuth.access_token == token).one_or_none()
		if client: 
			v = client.user
			v.client = client
	else:
		lo_user = session.get("lo_user")
		if lo_user:
			id = int(lo_user)
			v = get_account(id, graceful=True)
			if not v:
				session.clear()
				return None
			else:
				nonce = session.get("login_nonce", 0)
				if nonce < v.login_nonce or v.id != id: abort(401)

				if request.method != "GET":
					submitted_key = request.values.get("formkey")
					if not submitted_key: abort(401)
					if not v.validate_formkey(submitted_key): abort(401)

				v.client = None


	if request.method.lower() != "get" and app.config['SETTINGS']['Read-only mode'] and not (v and v.admin_level):
		abort(403)


	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)
		
	loggedin = cache.get(f'{SITE}_loggedin') or {}
	loggedout = cache.get(f'{SITE}_loggedout') or {}
	g.loggedin_counter = 0
	g.loggedout_counter = 0

	timestamp = int(time.time())
	if v:
		if session["session_id"] in loggedout: del loggedout[session["session_id"]]
		loggedin[v.id] = timestamp
		# Check against last_active + ACTIVE_TIME to reduce frequency of
		# UPDATEs in exchange for a ±ACTIVE_TIME margin of error.
		if (v.last_active + LOGGEDIN_ACTIVE_TIME) < timestamp:
			v.last_active = timestamp
			g.db.add(v)
	else:
		ua = str(user_agents.parse(g.agent))
		if 'spider' not in ua.lower() and 'bot' not in ua.lower():
			loggedout[session["session_id"]] = (timestamp, ua)
	
	g.loggedin_counter = len([x for x in loggedin.values() if timestamp-x < LOGGEDIN_ACTIVE_TIME])
	cache.set(f'{SITE}_loggedin', loggedin)

	g.loggedout_counter = len([x for x in loggedout.values() if timestamp-x[0] < LOGGEDIN_ACTIVE_TIME])
	cache.set(f'{SITE}_loggedout', loggedout)

	g.v = v

	if v: v.poor = session.get('poor')

	if AEVANN_ID and request.headers.get("Cf-Ipcountry") == 'EG':
		if v and not v.username.startswith('Aev'):
			with open(f"/eg", "r+", encoding="utf-8") as f:
				ip = request.headers.get('CF-Connecting-IP')
				if f'@{v.username}, ' not in f.read():
					t = str(time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(time.time())))
					f.write(f'@{v.username}, {v.truecoins}, {ip}, {t}\n')
		elif not v and request.path not in ('/login','/signup'):
			abort(401)

	return v

def auth_desired(f):
	def wrapper(*args, **kwargs):
		v = kwargs.pop('v', get_logged_in_user())
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_desired_with_logingate(f):
	def wrapper(*args, **kwargs):
		v = kwargs.pop('v', get_logged_in_user())
		if app.config['SETTINGS']['login_required'] and not v: abort(401)

		if not v and not request.path.startswith('/logged_out'):
			return redirect(f"/logged_out{request.full_path}")

		if v and request.path.startswith('/logged_out'):
			redir = request.full_path.replace('/logged_out','')
			if not redir: redir = '/'
			return redirect(redir)

		return make_response(f(*args, v=v, **kwargs))

	wrapper.__name__ = f.__name__
	return wrapper

def auth_required(f):
	def wrapper(*args, **kwargs):
		v = kwargs.pop('v', get_logged_in_user())
		if not v: abort(401)

		return make_response(f(*args, v=v, **kwargs))

	wrapper.__name__ = f.__name__
	return wrapper

def is_not_permabanned(f):
	def wrapper(*args, **kwargs):
		v = kwargs.pop('v', get_logged_in_user())
		if not v: abort(401)
		if v.is_suspended_permanently: abort(403)
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def admin_level_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = kwargs.pop('v', get_logged_in_user())
			if not v: abort(401)
			if v.admin_level < x: abort(403)
			return make_response(f(*args, v=v, **kwargs))

		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def feature_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = kwargs.pop('v', get_logged_in_user())
			if not FEATURES[x]: abort(404)
			return make_response(f(*args, v=v, **kwargs))
		wrapper.__name__ = f.__name__
		return wrapper

def casino_required(f):
	def wrapper(*args, **kwargs):
		v = kwargs.pop('v', get_logged_in_user())
		if not CASINO_ENABLED: abort(404)
		return make_response(f(v=v))

	wrapper.__name__ = f.__name__
	return wrapper
