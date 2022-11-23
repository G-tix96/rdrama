import gevent.monkey

gevent.monkey.patch_all()

import faulthandler
from os import environ
from sys import argv, stdout

import gevent
import redis
from flask import Flask
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker

from files.helpers.const import *
from files.helpers.const_stateful import const_initialize
from files.helpers.settings import reload_settings, start_watching_settings

print("fsdfsd")

app = Flask(__name__, template_folder='templates')
app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.auto_reload = True
app.jinja_env.add_extension('jinja2.ext.do')
faulthandler.enable()

app.config['SERVER_NAME'] = SITE
app.config['SECRET_KEY'] = environ.get('SECRET_KEY').strip()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3153600
if not IS_LOCALHOST:
	app.config['SESSION_COOKIE_DOMAIN'] = f'.{SITE}'
	app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_NAME"] = "session_" + environ.get("SITE_NAME").strip().lower()
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 365
app.config['SESSION_REFRESH_EACH_REQUEST'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URL'] = environ.get("DATABASE_URL").strip()

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = environ.get("REDIS_URL").strip()

r=redis.Redis(host=environ.get("REDIS_URL").strip(), decode_responses=True, ssl_cert_reqs=None)

def get_CF():
	with app.app_context():
		return request.headers.get('CF-Connecting-IP')

limiter = Limiter(
	app,
	key_func=get_CF,
	default_limits=[DEFAULT_RATELIMIT],
	application_limits=["10/second;200/minute;5000/hour;10000/day"],
	storage_uri=environ.get("REDIS_URL", "redis://localhost")
)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URL'])

db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

const_initialize(db_session)

reload_settings()
start_watching_settings()

cache = Cache(app)
Compress(app)

from files.routes.allroutes import *

@limiter.request_filter
def no_step_on_jc():
	if request:
		key = environ.get("NO_STEP_ON_JC", "")
		if key and key == request.headers.get("X-No-Step", ""): return True
	return False

if "load_chat" in argv:
	from files.routes.chat import *
else:
	from files.routes import *

stdout.flush()
