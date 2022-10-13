import gevent.monkey
gevent.monkey.patch_all()
from os import environ, path
import secrets
from flask import *
from flask_caching import Cache
from flask_limiter import Limiter
from flask_compress import Compress
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import *
import gevent
import redis
import time
from sys import stdout, argv
import faulthandler
import json
import random

app = Flask(__name__, template_folder='templates')
app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.auto_reload = True
app.jinja_env.add_extension('jinja2.ext.do')
faulthandler.enable()

app.config['SECRET_KEY'] = environ.get('SECRET_KEY').strip()
app.config["SERVER_NAME"] = environ.get("SITE").strip()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3153600
app.config["SESSION_COOKIE_NAME"] = "session_" + environ.get("SITE_NAME").strip().lower()
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 365
app.config['SESSION_REFRESH_EACH_REQUEST'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URL'] = environ.get("DATABASE_URL").strip()

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = environ.get("REDIS_URL").strip()


app.config['SETTINGS'] = {}

r=redis.Redis(host=environ.get("REDIS_URL").strip(), decode_responses=True, ssl_cert_reqs=None)

def get_CF():
	with app.app_context():
		return request.headers.get('CF-Connecting-IP')

limiter = Limiter(
	app,
	key_func=get_CF,
	default_limits=["3/second;30/minute;200/hour;1000/day"],
	application_limits=["10/second;200/minute;5000/hour;10000/day"],
	storage_uri=environ.get("REDIS_URL", "redis://localhost")
)

Base = declarative_base()

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URL'])

db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

cache = Cache(app)
Compress(app)

if not path.isfile(f'/site_settings.json'):
	with open('/site_settings.json', 'w', encoding='utf_8') as f:
		f.write(
			'{"Bots": true, "Fart mode": false, "Read-only mode": false, ' + \
			'"Signups": true, "login_required": false}')

@app.before_request
def before_request():

	g.agent = request.headers.get("User-Agent")
	if not g.agent and request.path != '/kofi':
		return 'Please use a "User-Agent" header!', 403

	ua = g.agent or ''
	ua = ua.lower()

	with open('/site_settings.json', 'r', encoding='utf_8') as f:
		app.config['SETTINGS'] = json.load(f)

	if request.host != app.config["SERVER_NAME"]: return {"error": "Unauthorized host provided."}, 403
	if request.headers.get("CF-Worker"): return {"error": "Cloudflare workers are not allowed to access this website."}, 403

	if not app.config['SETTINGS']['Bots'] and request.headers.get("Authorization"): abort(403)

	g.db = db_session()
	g.webview = '; wv) ' in ua
	g.inferior_browser = 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua or ' firefox/' in ua

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

@app.after_request
def after_request(response):
	response.headers.add("Strict-Transport-Security", "max-age=31536000")
	response.headers.add("X-Frame-Options", "deny")
	if response.status_code < 400:
		g.db.commit()
		g.db.close()
		del g.db
	return response

@app.teardown_appcontext
def teardown_request(error):
	if hasattr(g, 'db') and g.db:
		g.db.rollback()
		g.db.close()
		del g.db
	stdout.flush()

if "load_chat" in argv:
	from files.routes.chat import *
else:
	from files.routes import *

stdout.flush()
