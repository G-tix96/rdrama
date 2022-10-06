from files.helpers.wrappers import *
from files.helpers.get import *
from files.helpers.alerts import *
from flask import g
from files.__main__ import app, limiter
from os import path
from files.helpers.sanitize import filter_emojis_only

@app.post("/report/post/<pid>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def flag_post(pid, v):

	post = get_post(pid)

	reason = request.values.get("reason", "").strip()

	if blackjack and any(i in reason.lower() for i in blackjack.split()):
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = 'Blackjack'
		send_repeatable_notification(CARP_ID, f"reports on {post.permalink}")

	if v.is_muted:
		return {"error": "You are forbidden from making reports."}, 400

	reason = reason[:100]

	reason = filter_emojis_only(reason)

	if len(reason) > 350: return {"error": "Too long."}, 400

	if reason.startswith('!') and (v.admin_level > PERMS['POST_COMMENT_MODERATION'] or post.sub and v.mods(post.sub)):
		post.flair = reason[1:]
		g.db.add(post)
		if v.admin_level > 1:
			ma=ModAction(
				kind="flair_post",
				user_id=v.id,
				target_submission_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
		else:
			ma = SubAction(
				sub=post.sub,
				kind="flair_post",
				user_id=v.id,
				target_submission_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)

	elif reason.startswith('/h/') and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == post.author_id or (reason == '/h/chudrama' and v.mods(post.sub))):

		sub_from = post.sub
		sub_to = reason[3:].strip().lower()
		sub_to = g.db.get(Sub, sub_to)
		sub_to = sub_to.name if sub_to else None

		if sub_from == sub_to: {"error": f"Post is already in /h/{sub_to}"}, 400
		
		if post.author.exiled_from(sub_to):
			return {"error": f"User is exiled from this {HOLE_NAME}!"}, 400

		if sub_to in ('furry','vampire','racist','femboy') and not v.client and not post.author.house.lower().startswith(sub_to):
			if v.id == post.author_id:
				return {"error": f"You need to be a member of House {sub.capitalize()} to post in /h/{sub}"}, 403
			else:
				return {"error": f"@{post.author.username} needs to be a member of House {sub.capitalize()} for their post to be moved to /h/{sub}"}, 400

		post.sub = sub_to
		g.db.add(post)

		if v.id != post.author_id:
			if v.admin_level:
				sub_from_str = 'main feed' if sub_from is None else \
					f'<a href="/h/{sub_from}">/h/{sub_from}</a>'
				sub_to_str = 'main feed' if sub_to is None else \
					f'<a href="/h/{sub_to}">/h/{sub_to}</a>'
				ma = ModAction(
					kind='move_hole',
					user_id=v.id,
					target_submission_id=post.id,
					_note=f'{sub_from_str} → {sub_to_str}',
				)
				g.db.add(ma)
			else:
				ma = SubAction(
					sub=sub_from,
					kind='move_chudrama',
					user_id=v.id,
					target_submission_id=post.id
				)
				g.db.add(ma)

		if v.id != post.author_id:
			if v.admin_level >= 3: position = 'Admin'
			else: position = 'Mod'
			message = f"@{v.username} ({position}) has moved [{post.title}]({post.shortlink}) to /h/{post.sub}"
			send_repeatable_notification(post.author_id, message)

		return {"message": f"Post moved to /h/{post.sub}"}
	else:
		existing = g.db.query(Flag.post_id).filter_by(user_id=v.id, post_id=post.id).one_or_none()
		if existing:
			return {"error": "You already reported this post!"}, 409
		flag = Flag(post_id=post.id, user_id=v.id, reason=reason)
		g.db.add(flag)


	return {"message": "Post reported!"}


@app.post("/report/comment/<cid>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def flag_comment(cid, v):

	comment = get_comment(cid)
	
	existing = g.db.query(CommentFlag.comment_id).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()
	if existing:
		return {"error": "You already reported this comment!"}, 409

	reason = request.values.get("reason", "").strip()

	if blackjack and any(i in reason.lower() for i in blackjack.split()):
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = 'Blackjack'
		send_repeatable_notification(CARP_ID, f"reports on {comment.permalink}")

	reason = reason[:100]

	reason = filter_emojis_only(reason)

	if len(reason) > 350: return {"error": "Too long."}, 400

	flag = CommentFlag(comment_id=comment.id, user_id=v.id, reason=reason)

	g.db.add(flag)

	return {"message": "Comment reported!"}


@app.post('/del_report/post/<pid>/<uid>')
@limiter.limit("4/second;100/minute;300/hour;2000/day")
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_post(v, pid, uid):

	try:
		pid = int(pid)
		uid = int(uid)
	except: abort(400)

	report = g.db.query(Flag).filter_by(post_id=pid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_submission_id=pid
		)

		g.db.add(ma)


	return {"message": "Report removed successfully!"}


@app.post('/del_report/comment/<cid>/<uid>')
@limiter.limit("4/second;100/minute;300/hour;2000/day")
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_comment(v, cid, uid):
	
	cid = int(cid)
	uid = int(uid)
	
	report = g.db.query(CommentFlag).filter_by(comment_id=cid, user_id=uid).one_or_none()
	
	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_comment_id=cid
		)

		g.db.add(ma)


	return {"message": "Report removed successfully!"}
