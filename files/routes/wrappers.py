import time
import secrets

import user_agents
from flask import g, request, session

from files.classes.clients import ClientAuth
from files.helpers.alerts import *
from files.helpers.const import *
from files.helpers.get import get_account
from files.helpers.settings import get_setting
from files.routes.routehelpers import validate_formkey
from files.__main__ import app, cache, db_session, limiter

def session_init():
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)

def calc_users(v):
	if g.is_api_or_xhr: 
		g.loggedin_counter = 0
		g.loggedout_counter = 0
		return ''
	loggedin = cache.get(f'{SITE}_loggedin') or {}
	loggedout = cache.get(f'{SITE}_loggedout') or {}
	timestamp = int(time.time())

	session_init()
	if v:
		if session["session_id"] in loggedout: del loggedout[session["session_id"]]
		loggedin[v.id] = timestamp
	else:
		ua = str(user_agents.parse(g.agent))
		if 'spider' not in ua.lower() and 'bot' not in ua.lower():
			loggedout[session["session_id"]] = (timestamp, ua)
	
	loggedin = {k: v for k, v in loggedin.items() if (timestamp - v) < LOGGEDIN_ACTIVE_TIME}
	loggedout = {k: v for k, v in loggedout.items() if (timestamp - v[0]) < LOGGEDIN_ACTIVE_TIME}
	cache.set(f'{SITE}_loggedin', loggedin)
	cache.set(f'{SITE}_loggedout', loggedout)

	g.loggedin_counter = len(loggedin)
	g.loggedout_counter = len(loggedout)
	return ''

def get_logged_in_user():
	if hasattr(g, 'v'): return g.v
	if not getattr(g, 'db', None): g.db = db_session()
	g.desires_auth = True
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
				session.pop("lo_user")
			else:
				nonce = session.get("login_nonce", 0)
				if nonce < v.login_nonce or v.id != id:
					session.pop("lo_user")
					v = None

				if v and request.method != "GET":
					submitted_key = request.values.get("formkey")
					if not validate_formkey(v, submitted_key): abort(401)

				v.client = None
	g.is_api_or_xhr = bool((v and v.client) or request.headers.get("xhr"))

	if request.method.lower() != "get" and get_setting('Read-only mode') and not (v and v.admin_level >= PERMS['SITE_BYPASS_READ_ONLY_MODE']):
		abort(403)

	g.v = v

	if v:
		v.poor = session.get('poor')
		# Check against last_active + ACTIVE_TIME to reduce frequency of
		# UPDATEs in exchange for a ±ACTIVE_TIME margin of error.
		timestamp = int(time.time())
		if (v.last_active + LOGGEDIN_ACTIVE_TIME) < timestamp:
			v.last_active = timestamp
			g.db.add(v)

	if AEVANN_ID and request.headers.get("Cf-Ipcountry") == 'EG':
		if v and not v.username.startswith('Aev') and v.truescore > 0:
			with open("/eg", "r+", encoding="utf-8") as f:
				ip = request.headers.get('CF-Connecting-IP')
				if f'@{v.username}, ' not in f.read():
					t = str(time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(time.time())))
					f.write(f'@{v.username}, {v.truescore}, {ip}, {t}\n')
	return v

def auth_desired(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_desired_with_logingate(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if get_setting('login_required') and not v: abort(401)

		if request.path.startswith('/logged_out'):
			redir = request.full_path.replace('/logged_out','')
			if not redir: redir = '/'
			return redirect(redir)

		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_required(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: abort(401)
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_permabanned(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: abort(401)
		if v.is_suspended_permanently: abort(403)
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def admin_level_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = get_logged_in_user()
			if not v: abort(401)
			if v.admin_level < x: abort(403)
			return make_response(f(*args, v=v, **kwargs))

		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def feature_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			if not FEATURES[x]: abort(404)
			return make_response(f(*args, **kwargs))
		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def ratelimit_user(limit:Union[str, Callable[[], str]]=DEFAULT_RATELIMIT_USER):
	'''
	Ratelimits based on a user. This requires at least auth_required (or stronger) to be present, 
	otherwise logged out users will receive 500s
	'''
	def inner(func):
		@functools.wraps(func)
		@limiter.limit(limit, key_func=lambda:f'{SITE}-{g.v.id}')
		def wrapped(*args, **kwargs):
			return func(*args, **kwargs)
		return wrapped
	return inner
