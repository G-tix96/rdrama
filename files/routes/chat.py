import atexit
import time
import uuid

from flask_socketio import SocketIO, emit, join_room, leave_room

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.regex import *
from files.helpers.media import process_image
from files.helpers.sanitize import sanitize
from files.helpers.alerts import push_notif
from files.routes.wrappers import *

from files.__main__ import app, cache, limiter

socketio = SocketIO(
	app,
	async_mode='gevent',
)

typing = {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/admin/chat': []
}
online =  []
cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)
muted = cache.get(f'muted') or {
	f'{SITE_FULL}/chat': {},
	f'{SITE_FULL}/admin/chat': {}
}
messages = cache.get(f'messages') or {
	f'{SITE_FULL}/chat': {},
	f'{SITE_FULL}/admin/chat': {}
}

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def chat(v):
	if not v.admin_level and TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		abort(403, f"Need at least {TRUESCORE_CHAT_MINIMUM} truescore for access to chat.")
	
	if v.id == 1: print(messages[f"{SITE_FULL}/chat"], flush=True)
	return 'aaaa'
	return render_template("chat.html", v=v, messages=messages[f"{SITE_FULL}/chat"])

@app.get("/admin/chat")
@admin_level_required(2)
def admin_chat(v):
	return render_template("chat.html", v=v, messages=messages[f"{SITE_FULL}/admin/chat"])

@socketio.on('speak')
@limiter.limit("3/second;10/minute")
@limiter.limit("3/second;10/minute", key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def speak(data, v):
	image = None
	if data['file']:
		name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
		with open(name, 'wb') as f:
			f.write(data['file'])
		image = process_image(name, v)

	limiter.check()
	if v.is_banned: return '', 403
	if TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		return '', 403

	vname = v.username.lower()
	if vname in muted[request.referrer] and not v.admin_level >= PERMS['CHAT_BYPASS_MUTE']:
		if time.time() < muted[request.referrer][vname]: return '', 403
		else: del muted[request.referrer][vname]

	global messages

	text = sanitize_raw_body(data['message'], False)[:CHAT_LENGTH_LIMIT]
	if image: text += f'\n\n![]({image})'
	if not text: return '', 400

	text_html = sanitize(text, count_marseys=True)
	quotes = data['quotes']
	id = str(uuid.uuid4())
	data = {
		"quotes": quotes,
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"text": text,
		"text_html": text_html,
		"text_censored": censor_slurs(text_html, 'chat'),
		"time": int(time.time()),
	}

	if v.shadowbanned or not execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, room=request.referrer, broadcast=True)
		messages[request.referrer][id] = data
		messages[request.referrer] = dict(list(messages[request.referrer].items())[-500:])

	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			duration = int(int(i.group(2)) * 60 + time.time())
			muted[request.referrer][username] = duration

	typing = []

	if request.referrer == f'{SITE_FULL}/admin/chat':
		title = f'New message in admin chat from @{v.username}'
		notifbody = text
		url = f'{SITE_FULL}/admin/chat'

		admin_ids = [x[0] for x in g.db.query(User.id).filter(
			User.id != v.id,
			User.admin_level >= 2,
		).all()]

		push_notif(admin_ids, title, notifbody, url)

	return '', 204

def refresh_online():
	emit("online", online, broadcast=True)
	if request.referrer == f'{SITE_FULL}/chat':
		cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)

@socketio.on('connect')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def connect(v):
	join_room(request.referrer)

	if v.username not in online:
		online.append(v.username)
		refresh_online()

	emit('typing', typing[request.referrer], room=request.referrer)
	return '', 204

@socketio.on('disconnect')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def disconnect(v):
	if v.username in online:
		online.remove(v.username)
		refresh_online()

	if v.username in typing[request.referrer]:
		typing[request.referrer].remove(v.username)

	emit('typing', typing[request.referrer], room=request.referrer, broadcast=True)

	leave_room(request.referrer)
	return '', 204

@socketio.on('typing')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def typing_indicator(data, v):

	if data and v.username not in typing[request.referrer]:
		typing[request.referrer].append(v.username)
	elif not data and v.username in typing[request.referrer]:
		typing[request.referrer].remove(v.username)

	emit('typing', typing[request.referrer], room=request.referrer, broadcast=True)
	return '', 204


@socketio.on('delete')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	for k, val in messages[request.referrer].items():
		if k == id:
			del messages[request.referrer][k]
			break

	emit('delete', id, room=request.referrer, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set(f'messages', messages)
	cache.set(f'muted', muted)
atexit.register(close_running_threads)
