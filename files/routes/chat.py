import atexit
import time
import uuid

from flask_socketio import SocketIO, emit, join_room, leave_room

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.regex import *
from files.helpers.sanitize import sanitize
from files.helpers.alerts import push_notif
from files.routes.wrappers import *

from files.__main__ import app, cache, limiter

if IS_LOCALHOST:
	socketio = SocketIO(
		app,
		async_mode='gevent',
		logger=True,
		engineio_logger=True,
		debug=True
	)
else:
	socketio = SocketIO(
		app,
		async_mode='gevent',
	)

typing = {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/admin/chat': []
}
online =  {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/admin/chat': []
}
cache.set(CHAT_ONLINE_CACHE_KEY, len(online[f'{SITE_FULL}/chat']), timeout=0)
muted = cache.get(f'muted') or {
	f'{SITE_FULL}/chat': {},
	f'{SITE_FULL}/admin/chat': {}
}
messages = cache.get(f'messages') or {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/admin/chat': []
}
socket_ids_to_user_ids = {}
user_ids_to_socket_ids = {}

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def chat(v):
	if not v.admin_level and TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		abort(403, f"Need at least {TRUESCORE_CHAT_MINIMUM} truescore for access to chat.")
	return render_template("chat.html", v=v)

@app.get("/admin/chat")
@admin_level_required(2)
def admin_chat(v):
	return render_template("chat.html", v=v)

@socketio.on('speak')
@limiter.limit("3/second;10/minute")
@limiter.limit("3/second;10/minute", key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def speak(data, v):
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
	if not text: return '', 400

	text_html = sanitize(text, count_marseys=True)
	quotes = data['quotes']
	recipient = data['recipient']
	data = {
		"id": str(uuid.uuid4()),
		"quotes": quotes,
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"dm": bool(recipient and recipient != ""),
		"username": v.username,
		"namecolor": v.name_color,
		"text": text,
		"text_html": text_html,
		"base_text_censored": censor_slurs(text, 'chat'),
		"text_censored": censor_slurs(text_html, 'chat'),
		"time": int(time.time()),
	}

	if v.shadowbanned or not execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	elif recipient:
		if user_ids_to_socket_ids.get(recipient):
			recipient_sid = user_ids_to_socket_ids[recipient]
			emit('speak', data, broadcast=False, to=recipient_sid)
	else:
		emit('speak', data, room=request.referrer, broadcast=True)
		messages[request.referrer].append(data)
		messages[request.referrer] = messages[request.referrer][-500:]

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
	emit("online", online[request.referrer], room=request.referrer, broadcast=True)
	if request.referrer == f'{SITE_FULL}/chat':
		cache.set(CHAT_ONLINE_CACHE_KEY, len(online[request.referrer]), timeout=0)

@socketio.on('connect')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def connect(v):
	join_room(request.referrer)

	if v.username not in online[request.referrer]:
		online[request.referrer].append(v.username)
		refresh_online()

	if not socket_ids_to_user_ids.get(request.sid):
		socket_ids_to_user_ids[request.sid] = v.id
		user_ids_to_socket_ids[v.id] = request.sid

	emit('catchup', messages[request.referrer], room=request.referrer)
	emit('typing', typing[request.referrer], room=request.referrer)
	return '', 204

@socketio.on('disconnect')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def disconnect(v):
	if v.username in online[request.referrer]:
		online[request.referrer].remove(v.username)
		refresh_online()

	if v.username in typing[request.referrer]:
		typing[request.referrer].remove(v.username)

	if socket_ids_to_user_ids.get(request.sid):
		del socket_ids_to_user_ids[request.sid]
		del user_ids_to_socket_ids[v.id]

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
def delete(text, v):

	for message in messages:
		if message['text'] == text:
			messages[request.referrer].remove(message)

	emit('delete', text, room=request.referrer, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set(f'messages', messages)
	cache.set(f'muted', muted)
atexit.register(close_running_threads)
