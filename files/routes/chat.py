import time
import uuid
from files.helpers.jinja2 import timestamp
from files.helpers.wrappers import *
from files.helpers.sanitize import sanitize
from files.helpers.const import *
from files.helpers.alerts import *
from files.helpers.regex import *
from flask_socketio import SocketIO, emit
from files.__main__ import app, limiter, cache
from flask import render_template
import sys
import atexit

if SITE == 'localhost':
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

typing = []
online = []
cache.set(ONLINE_STR, len(online), timeout=0)
muted = cache.get(f'{SITE}_muted') or {}
messages = cache.get(f'{SITE}_chat') or []
total = cache.get(f'{SITE}_total') or 0
socket_ids_to_user_ids = {}
user_ids_to_socket_ids = {}

@app.get("/chat")
@is_not_permabanned
def chat(v):
	return render_template("chat.html", v=v, messages=messages)


@socketio.on('speak')
@limiter.limit("3/second;10/minute")
@limiter.limit("3/second;10/minute", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def speak(data, v):
	if v.is_banned: return '', 403

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]: return '', 403
		else: del muted[vname]

	global messages, total

	if SITE == 'rdrama.net': text = data['message'][:200].strip()
	else: text = data['message'][:1000].strip()

	if not text: return '', 403
	text_html = sanitize(text, count_marseys=True)
	quotes = data['quotes']
	recipient = data['recipient']
	data={
		"id": str(uuid.uuid4()),
		"quotes": quotes,
		"avatar": v.profile_url,
		"hat": v.hat_active,
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
	
	if v.shadowbanned:
		emit('speak', data)
	elif blackjack and any(i in text.lower() for i in blackjack.split()):
		emit('speak', data)
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = 'Blackjack'
		g.db.add(v)
		send_repeatable_notification(CARP_ID, f"{v.username} has been shadowbanned because of a chat message.")
	elif recipient:
		if user_ids_to_socket_ids.get(recipient):
			recipient_sid = user_ids_to_socket_ids[recipient]
			emit('speak', data, broadcast=False, to=recipient_sid)
	else:
		emit('speak', data, broadcast=True)
		messages.append(data)
		messages = messages[-100:]

	total += 1

	if v.admin_level > 1:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			duration = int(int(i.group(2)) * 60 + time.time())
			muted[username] = duration

	typing = []
	return '', 204

@socketio.on('connect')
@is_not_permabanned
def connect(v):
	if v.username not in online:
		online.append(v.username)
		emit("online", online, broadcast=True)
		cache.set(ONLINE_STR, len(online), timeout=0)

	if not socket_ids_to_user_ids.get(request.sid):
		socket_ids_to_user_ids[request.sid] = v.id
		user_ids_to_socket_ids[v.id] = request.sid

	emit('online', online)
	emit('catchup', messages)
	emit('typing', typing)
	return '', 204

@socketio.on('disconnect')
@is_not_permabanned
def disconnect(v):
	if v.username in online:
		online.remove(v.username)
		emit("online", online, broadcast=True)
		cache.set(ONLINE_STR, len(online), timeout=0)

	if v.username in typing: typing.remove(v.username)

	if socket_ids_to_user_ids.get(request.sid):
		del socket_ids_to_user_ids[request.sid]
		del user_ids_to_socket_ids[v.id]

	emit('typing', typing, broadcast=True)
	return '', 204

@socketio.on('typing')
@is_not_permabanned
def typing_indicator(data, v):

	if data and v.username not in typing: typing.append(v.username)
	elif not data and v.username in typing: typing.remove(v.username)

	emit('typing', typing, broadcast=True)
	return '', 204


@socketio.on('delete')
@admin_level_required(2)
def delete(text, v):

	for message in messages:
		if message['text'] == text:
			messages.remove(message)

	emit('delete', text, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set(f'{SITE}_chat', messages)
	cache.set(f'{SITE}_total', total)
	cache.set(f'{SITE}_muted', muted)
atexit.register(close_running_threads)
