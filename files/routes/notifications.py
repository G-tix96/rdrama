from files.helpers.wrappers import *
from files.helpers.get import *
from files.helpers.const import *
from files.__main__ import app
import time

@app.post("/clear")
@auth_required
def clear(v):
	notifs = g.db.query(Notification).join(Notification.comment).filter(Notification.read == False, Notification.user_id == v.id).all()
	for n in notifs:
		n.read = True
		g.db.add(n)
	v.last_viewed_post_notifs = int(time.time())
	v.last_viewed_log_notifs = int(time.time())
	g.db.add(v)
	return {"message": "Notifications marked as read!"}


@app.get("/unread")
@auth_required
def unread(v):
	listing = g.db.query(Notification, Comment).join(Notification.comment).filter(
		Notification.read == False,
		Notification.user_id == v.id,
		Comment.is_banned == False,
		Comment.deleted_utc == 0,
	).order_by(Notification.created_utc.desc()).all()

	for n, c in listing:
		n.read = True
		g.db.add(n)

	return {"data":[x[1].json for x in listing]}



@app.get("/notifications/modmail")
@admin_level_required(PERMS['VIEW_MODMAIL'])
def notifications_modmail(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	comments = g.db.query(Comment).filter(Comment.sentto==2).order_by(Comment.id.desc()).offset(25*(page-1)).limit(26).all()
	next_exists = (len(comments) > 25)
	listing = comments[:25]

	g.db.commit()

	if request.headers.get("Authorization"): return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)



@app.get("/notifications/messages")
@auth_required
def notifications_messages(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	# All of these queries are horrible. For whomever comes here after me,
	# PLEASE just turn DMs into their own table and get them out of
	# Notifications & Comments. It's worth it. Save yourself.
	message_threads = g.db.query(Comment).filter(
		Comment.sentto != None,
		or_(Comment.author_id == v.id, Comment.sentto == v.id),
		Comment.parent_submission == None,
		Comment.level == 1,
	)
	if not v.shadowbanned and v.admin_level < PERMS['NOTIFICATIONS_FROM_SHADOWBANNED_USERS']:
		message_threads = message_threads.join(Comment.author) \
							.filter(User.shadowbanned == None)

	thread_order = g.db.query(Comment.top_comment_id, Comment.created_utc) \
		.distinct(Comment.top_comment_id) \
		.filter(
			Comment.sentto != None,
			or_(Comment.author_id == v.id, Comment.sentto == v.id),
		).order_by(
			Comment.top_comment_id.desc(),
			Comment.created_utc.desc()
		).subquery()

	message_threads = message_threads.join(thread_order,
						thread_order.c.top_comment_id == Comment.top_comment_id)
	message_threads = message_threads.order_by(thread_order.c.created_utc.desc()) \
						.offset(25*(page-1)).limit(26).all()

	# Clear notifications (used for unread indicator only) for all user messages.
	notifs_unread_row = g.db.query(Notification.comment_id).join(Comment).filter(
		Notification.user_id == v.id,
		Notification.read == False,
		or_(Comment.author_id == v.id, Comment.sentto == v.id),
	).all()

	notifs_unread = [n.comment_id for n in notifs_unread_row]
	g.db.query(Notification).filter(
			Notification.user_id == v.id,
			Notification.comment_id.in_(notifs_unread),
		).update({Notification.read: True})
	g.db.commit()

	next_exists = (len(message_threads) > 25)
	listing = message_threads[:25]

	list_to_perserve_unread_attribute = []
	comments_unread = g.db.query(Comment).filter(Comment.id.in_(notifs_unread))
	for c in comments_unread:
		c.unread = True
		list_to_perserve_unread_attribute.append(c)

	if request.headers.get("Authorization"): return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notifications/posts")
@auth_required
def notifications_posts(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	listing = [x[0] for x in g.db.query(Submission.id).filter(
		or_(
			Submission.author_id.in_(v.followed_users),
			Submission.sub.in_(v.followed_subs)
		),
		Submission.deleted_utc == 0,
		Submission.is_banned == False,
		Submission.private == False,
		Submission.notify == True,
		Submission.author_id != v.id,
		Submission.ghost == False,
		Submission.author_id.notin_(v.userblocks)
	).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()]

	next_exists = (len(listing) > 25)
	listing = listing[:25]
	listing = get_posts(listing, v=v)

	for p in listing:
		p.unread = p.created_utc > v.last_viewed_post_notifs

	v.last_viewed_post_notifs = int(time.time())
	g.db.add(v)

	if request.headers.get("Authorization"): return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notifications/modactions")
@admin_level_required(NOTIF_MODACTION_JL_MIN)
def notifications_modactions(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	listing = g.db.query(ModAction).filter(ModAction.user_id != v.id).order_by(ModAction.id.desc()).offset(25*(page-1)).limit(26).all()

	next_exists = len(listing) > 25
	listing = listing[:25]

	for ma in listing:
		ma.unread = ma.created_utc > v.last_viewed_log_notifs

	v.last_viewed_log_notifs = int(time.time())
	g.db.add(v)

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)



@app.get("/notifications/reddit")
@auth_required
def notifications_reddit(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	if not v.can_view_offsitementions: abort(403)

	notifications = g.db.query(Notification, Comment).join(Notification.comment).filter(
		Notification.user_id == v.id,
		Comment.body_html.like('%<p>New site mention%<a href="https://old.reddit.com/r/%'),
		Comment.parent_submission == None,
		Comment.author_id == AUTOJANNY_ID
	).order_by(Notification.created_utc.desc()).offset(25 * (page - 1)).limit(101).all()

	listing = []

	for index, x in enumerate(notifications[:100]):
		n, c = x
		if n.read and index > 24: break
		elif not n.read:
			n.read = True
			c.unread = True
			g.db.add(n)
		if n.created_utc > 1620391248: c.notif_utc = n.created_utc
		listing.append(c)

	next_exists = (len(notifications) > len(listing))

	g.db.commit()

	if request.headers.get("Authorization"): return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)




@app.get("/notifications")
@auth_required
def notifications(v):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	comments = g.db.query(Comment, Notification).join(Notification.comment).filter(
		Notification.user_id == v.id,
		Comment.is_banned == False,
		Comment.deleted_utc == 0,
		Comment.body_html.notlike('%<p>New site mention%<a href="https://old.reddit.com/r/%'),
		or_(Comment.sentto == None, Comment.sentto == 2),
	).order_by(Notification.created_utc.desc())

	if not (v and (v.shadowbanned or v.admin_level >= PERMS['NOTIFICATIONS_FROM_SHADOWBANNED_USERS'])):
		comments = comments.join(Comment.author).filter(User.shadowbanned == None)

	comments = comments.offset(25 * (page - 1)).limit(26).all()

	next_exists = (len(comments) > 25)
	comments = comments[:25]

	cids = [x[0].id for x in comments]

	comms = get_comments(cids, v=v)

	listing = []
	for c, n in comments:
		if n.created_utc > 1620391248: c.notif_utc = n.created_utc
		if not n.read:
			n.read = True
			c.unread = True
			g.db.add(n)

		if c.parent_submission:
			if c.replies2 == None:
				c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
				for x in c.replies2:
					if x.replies2 == None: x.replies2 = []
			count = 0
			while count < 50 and c.parent_comment and (c.parent_comment.author_id == v.id or c.parent_comment.id in cids):
				count += 1
				c = c.parent_comment
				if c.replies2 == None:
					c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
					for x in c.replies2:
						if x.replies2 == None:
							x.replies2 = g.db.query(Comment).filter_by(parent_comment_id=x.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
		else:
			while c.parent_comment:
				c = c.parent_comment
			c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).order_by(Comment.id).all()

		if c not in listing: listing.append(c)

	g.db.commit()

	if request.headers.get("Authorization"): return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							next_exists=next_exists,
							page=page,
							standalone=True,
							render_replies=True,
						)
