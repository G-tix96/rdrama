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
muted = cache.get(f'muted') or {}
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
	return render_template("chat.html", v=v, messages=messages[f"{SITE_FULL}/chat"])

@app.get("/admin/chat")
@admin_level_required(2)
def admin_chat(v):
	return render_template("chat.html", v=v, messages=messages[f"{SITE_FULL}/admin/chat"])

@socketio.on('speak')
@admin_level_required(PERMS['CHAT'])
def speak(data, v):
	if not request.referrer:
		return '', 400

	image = None
	if data['file']:
		name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
		with open(name, 'wb') as f:
			f.write(data['file'])
		image = process_image(name, v)

	if v.is_banned: return '', 403
	if TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		return '', 403

	global messages

	text = sanitize_raw_body(data['message'], False)[:CHAT_LENGTH_LIMIT]
	if image: text += f'\n\n![]({image})'
	if not text: return '', 400

	text_html = sanitize(text, count_marseys=True)
	quotes = data['quotes']
	id = str(uuid.uuid4())

	self_only = False

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]:
			self_only = True
		else:
			del muted[vname]
			emit("online", [online, muted], broadcast=True)

	if SITE == 'rdrama.net':
		def shut_up():
			self_only = True
			muted_until = int(time.time() + 3600)
			muted[vname] = muted_until
			emit("online", [online, muted], broadcast=True)

		if not self_only:
			identical = [x for x in list(messages[request.referrer].values())[-5:] if v.id == x['user_id'] and text == x['text']]
			if len(identical) >= 3: shut_up()

		if not self_only:
			count = len([x for x in list(messages[request.referrer].values())[-12:] if v.id == x['user_id']])
			if count >= 10: shut_up()

		if not self_only:
			count = len([x for x in list(messages[request.referrer].values())[-25:] if v.id == x['user_id']])
			if count >= 20: shut_up()

	data = {
		"id": id,
		"quotes": quotes if messages[request.referrer].get(quotes) else '',
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"text": text,
		"text_html": text_html,
		"text_censored": censor_slurs(text_html, 'chat'),
		"time": int(time.time()),
	}


	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			muted_until = int(int(i.group(2)) * 60 + time.time())
			muted[username] = muted_until
			emit("online", [online, muted], broadcast=True)
			self_only = True

	if self_only or v.shadowbanned or not execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, room=request.referrer, broadcast=True)
		messages[request.referrer][id] = data
		messages[request.referrer] = dict(list(messages[request.referrer].items())[-500:])

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
	emit("online", [online, muted], broadcast=True)
	if request.referrer == f'{SITE_FULL}/chat':
		cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)

@socketio.on('connect')
@admin_level_required(PERMS['CHAT'])
def connect(v):
	if not request.referrer:
		return '', 400

	join_room(request.referrer)

	if v.username not in online:
		online.append(v.username)
		refresh_online()

	emit('typing', typing[request.referrer], room=request.referrer)
	return '', 204

@socketio.on('disconnect')
@admin_level_required(PERMS['CHAT'])
def disconnect(v):
	if v.username in online:
		online.remove(v.username)
		refresh_online()

	for val in typing.values():
		if v.username in val:
			val.remove(v.username)

	if request.referrer:
		leave_room(request.referrer)
	
	return '', 204

@socketio.on('typing')
@admin_level_required(PERMS['CHAT'])
def typing_indicator(data, v):
	if not request.referrer:
		return '', 400

	if data and v.username not in typing[request.referrer]:
		typing[request.referrer].append(v.username)
	elif not data and v.username in typing[request.referrer]:
		typing[request.referrer].remove(v.username)

	emit('typing', typing[request.referrer], room=request.referrer, broadcast=True)
	return '', 204


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	if not request.referrer:
		return '', 400

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
