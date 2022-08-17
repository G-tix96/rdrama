from files.classes import *
from flask import g
from .sanitize import *
from .const import *
from .regex import *
from pusher_push_notifications import PushNotifications
from sys import stdout

def create_comment(text_html):
	new_comment = Comment(author_id=AUTOJANNY_ID,
							parent_submission=None,
							body_html=text_html,
							distinguish_level=6,
							is_bot=True)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification(uid, text):

	if uid in bots: return

	text_html = sanitize(text)

	existing_comment = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_submission=None, body_html=text_html, is_bot=True).first()

	if existing_comment:
		cid = existing_comment[0]
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=cid).one_or_none()
		if existing_notif: cid = create_comment(text_html)
	else: cid = create_comment(text_html)

	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)


def send_notification(uid, text):

	if uid in bots: return
	cid = notif_comment(text)
	add_notif(cid, uid)


def notif_comment(text):

	text_html = sanitize(text)

	existing = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_submission=None, body_html=text_html, is_bot=True).one_or_none()

	if existing: return existing[0]
	else: return create_comment(text_html)


def notif_comment2(p):

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}">%'

	existing = g.db.query(Comment.id).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_submission == None, Comment.body_html.like(search_html)).first()
	
	if existing: return existing[0]
	else:
		text = f"@{p.author.username} has mentioned you: [{p.title}](/post/{p.id})"
		if p.sub: text += f" in <a href='/h/{p.sub}'>/h/{p.sub}"
		text_html = sanitize(text)
		return create_comment(text_html)


def add_notif(cid, uid):
	if uid in bots: return

	existing = g.db.query(Notification.user_id).filter_by(comment_id=cid, user_id=uid).one_or_none()
	if not existing:
		notif = Notification(comment_id=cid, user_id=uid)
		g.db.add(notif)


def NOTIFY_USERS(text, v):
	# Restrict young accounts from generating notifications
	if v.age < NOTIFICATION_SPAM_AGE_THRESHOLD:
		return set()

	notify_users = set()
	for word, id in NOTIFIED_USERS.items():
		if id == 0 or v.id == id: continue
		if word in text.lower() and id not in notify_users: notify_users.add(id)

	captured = []
	for i in mention_regex.finditer(text):
		if v.username.lower() == i.group(2).lower(): continue

		if i.group(0) in captured: continue
		captured.append(i.group(0))

		user = get_user(i.group(2), graceful=True)
		if user and v.id != user.id and not v.any_block_exists(user): notify_users.add(user.id)

	return notify_users - bots

if PUSHER_ID != 'blahblahblah':
	beams_client = PushNotifications(instance_id=PUSHER_ID, secret_key=PUSHER_KEY)

	def pusher_thread(interests, title, notifbody, url):
		title = censor_slurs(title, None)
		notifbody = censor_slurs(notifbody, None)

		beams_client.publish_to_interests(
			interests=[interests],
			publish_body={
				'web': {
					'notification': {
						'title': title,
						'body': notifbody,
						'deep_link': url,
						'icon': f'{SITE_FULL}/assets/images/{SITE_NAME}/icon.webp?v=3000',
					}
				},
				'fcm': {
					'notification': {
						'title': title,
						'body': notifbody,
					},
					'data': {
						'url': url,
					}
				}
			},
		)
		stdout.flush()