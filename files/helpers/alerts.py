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

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_submission=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

	for c in existing_comments:
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=c.id).one_or_none()
		if not existing_notif:
			notif = Notification(comment_id=c.id, user_id=uid)
			g.db.add(notif)
			return

	cid = create_comment(text_html)
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

	names = set(m.group(2) for m in mention_regex.finditer(text))
	for user in get_users(names, graceful=True):
		if v.id != user.id and not v.any_block_exists(user):
			notify_users.add(user.id)

	if SITE_NAME == "WPD" and 'daisy' in text.lower():
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_FOR_SPECIFIC_WPD_COMMENTS']).all()]
		notify_users.update(admin_ids)

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
						'icon': f'{SITE_FULL}/assets/images/{SITE_NAME}/icon.webp?v=3009',
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
