from .get import *
from .alerts import *
from files.helpers.const import *
from files.__main__ import db_session
from random import randint
import user_agents

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
			v = g.db.query(User).filter_by(id=id).one_or_none()
			if v:
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
	else:
		loggedout[session["session_id"]] = (timestamp, str(user_agents.parse(request.headers.get("User-Agent"))))
	
	g.loggedin_counter = len([x for x in loggedin.values() if timestamp-x<15*60])
	cache.set(f'{SITE}_loggedin', loggedin)

	g.loggedout_counter = len([x for x in loggedout.values() if timestamp-x[0]<15*60])
	cache.set(f'{SITE}_loggedout', loggedout)

	g.v = v

	return v

def check_ban_evade(v):
	if v and not v.patron and v.admin_level < 2 and v.ban_evade and not v.unban_utc:
		v.shadowbanned = "AutoJanny"
		g.db.add(v)
		g.db.commit()

def auth_desired(f):
	def wrapper(*args, **kwargs):

		v = get_logged_in_user()

		check_ban_evade(v)

		return make_response(f(*args, v=v, **kwargs))

	wrapper.__name__ = f.__name__
	return wrapper


def auth_required(f):

	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: abort(401)

		check_ban_evade(v)

		return make_response(f(*args, v=v, **kwargs))

	wrapper.__name__ = f.__name__
	return wrapper


def is_not_permabanned(f):

	def wrapper(*args, **kwargs):

		v = get_logged_in_user()

		if not v: abort(401)
		
		check_ban_evade(v)

		if v.is_banned and v.unban_utc == 0:
			return {"error": "Interal server error"}, 500

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