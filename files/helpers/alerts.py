from files.classes import *
from flask import g
from .sanitize import *
from .const import *
from .regex import *
from pusher_push_notifications import PushNotifications
from sys import stdout

def create_comment(text_html, autojanny=False):
	if autojanny: author_id = AUTOJANNY_ID
	else: author_id = NOTIFICATIONS_ID

	new_comment = Comment(author_id=author_id,
							parent_submission=None,
							body_html=text_html,
							distinguish_level=6)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification(uid, text, autojanny=False):

	if uid in bots: return

	if autojanny: author_id = AUTOJANNY_ID
	else: author_id = NOTIFICATIONS_ID
	
	text_html = sanitize(text)

	existing_comment = g.db.query(Comment.id).filter_by(author_id=author_id, parent_submission=None, body_html=text_html).first()

	if existing_comment:
		cid = existing_comment[0]
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=cid).one_or_none()
		if existing_notif: cid = create_comment(text_html, autojanny)
	else: cid = create_comment(text_html, autojanny)

	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)


def send_notification(uid, text, autojanny=False):

	if uid in bots: return
	cid = notif_comment(text, autojanny)
	add_notif(cid, uid)


def notif_comment(text, autojanny=False):

	if autojanny:
		author_id = AUTOJANNY_ID
		alert = True
	else:
		author_id = NOTIFICATIONS_ID
		alert = False

	text_html = sanitize(text)

	try: existing = g.db.query(Comment.id).filter_by(author_id=author_id, parent_submission=None, body_html=text_html).one_or_none()
	except:
		existing = g.db.query(Comment).filter_by(author_id=author_id, parent_submission=None, body_html=text_html).all()
		

		notifs = g.db.query(Notification).filter(Notification.comment_id.in_([x.id for x in existing])).all()
		for c in notifs: g.db.delete(c)
		g.db.flush()

		
		for c in existing: g.db.delete(c)
		g.db.flush()
		existing = g.db.query(Comment.id).filter_by(author_id=author_id, parent_submission=None, body_html=text_html).one_or_none()
	
	if existing: return existing[0]
	else: return create_comment(text_html, autojanny)


def notif_comment2(p):

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}">%'

	existing = g.db.query(Comment.id).filter(Comment.author_id == NOTIFICATIONS_ID, Comment.parent_submission == None, Comment.body_html.like(search_html)).first()
	
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

def notify_mod_action(by_id, msg):
	body_html = sanitize(NOTIF_MODACTION_PREFIX + msg)
	new_comment = Comment(
		author_id=NOTIFICATIONS_ID,
		parent_submission=None,
		level=1,
		body_html=body_html,
		distinguish_level=6)
	g.db.add(new_comment)
	g.db.flush()
	new_comment.top_comment_id = new_comment.id

	send_to = g.db.query(User).filter(
		User.admin_level >= NOTIF_MODACTION_JL_MIN, User.id != by_id).all()
	for admin in send_to:
		notif = Notification(comment_id=new_comment.id, user_id=admin.id)
		g.db.add(notif)


if PUSHER_ID != 'blahblahblah':
	beams_client = PushNotifications(instance_id=PUSHER_ID, secret_key=PUSHER_KEY)

	def pusher_thread(interests, title, notifbody, url):
		beams_client.publish_to_interests(
			interests=[interests],
			publish_body={
				'web': {
					'notification': {
						'title': title,
						'body': notifbody,
						'deep_link': url,
						'icon': f'{SITE_FULL}/assets/images/{SITE_NAME}/icon.webp?v=1015',
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



def on_post_hole_entered(post, v=None):
	if not post.sub or not post.subr:
		return
	hole = post.subr.name
	author = post.author

	# Notify hole followers
	if not post.ghost and not post.private and not author.shadowbanned:
		text = f"<a href='/h/{hole}'>/h/{hole}</a> has a new " \
			 + f"post: [{post.title}]({post.shortlink}) by @{author.username}"
		cid = notif_comment(text, autojanny=True)
		for follow in post.subr.followers:
			if follow.user_id == author.id or (v and follow.user_id == v.id):
				continue
			user = get_account(follow.user_id)
			if post.club and not user.paid_dues: continue
			add_notif(cid, user.id)