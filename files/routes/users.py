import qrcode
import io
import time
import math
from files.classes.views import *
from files.classes.transactions import *
from files.helpers.alerts import *
from files.helpers.sanitize import *
from files.helpers.const import *
from files.helpers.sorting_and_time import *
from files.mail import *
from flask import *
from files.__main__ import app, limiter, db_session
import sqlalchemy
from sqlalchemy.orm import aliased
from sqlalchemy import text
from collections import Counter
import gevent
from sys import stdout
import os
import json
from .login import check_for_alts


@app.get("/@<username>/upvoters/<uid>/posts")
@auth_required
def upvoters_posts(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==1, Submission.author_id==id, Vote.user_id==uid).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_posts(listing, v=v)

	return render_template("voted_posts.html", next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/@<username>/upvoters/<uid>/comments")
@auth_required
def upvoters_comments(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==1, Comment.author_id==id, CommentVote.user_id==uid).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_comments(listing, v=v)

	return render_template("voted_comments.html", next_exists=next_exists, listing=listing, page=page, v=v, standalone=True)


@app.get("/@<username>/downvoters/<uid>/posts")
@auth_required
def downvoters_posts(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==-1, Submission.author_id==id, Vote.user_id==uid).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_posts(listing, v=v)

	return render_template("voted_posts.html", next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/@<username>/downvoters/<uid>/comments")
@auth_required
def downvoters_comments(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==-1, Comment.author_id==id, CommentVote.user_id==uid).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_comments(listing, v=v)

	return render_template("voted_comments.html", next_exists=next_exists, listing=listing, page=page, v=v, standalone=True)





@app.get("/@<username>/upvoting/<uid>/posts")
@auth_required
def upvoting_posts(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==1, Vote.user_id==id, Submission.author_id==uid).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_posts(listing, v=v)

	return render_template("voted_posts.html", next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/@<username>/upvoting/<uid>/comments")
@auth_required
def upvoting_comments(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==1, CommentVote.user_id==id, Comment.author_id==uid).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_comments(listing, v=v)

	return render_template("voted_comments.html", next_exists=next_exists, listing=listing, page=page, v=v, standalone=True)


@app.get("/@<username>/downvoting/<uid>/posts")
@auth_required
def downvoting_posts(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==-1, Vote.user_id==id, Submission.author_id==uid).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_posts(listing, v=v)

	return render_template("voted_posts.html", next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/@<username>/downvoting/<uid>/comments")
@auth_required
def downvoting_comments(v, username, uid):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	uid = int(uid)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==-1, CommentVote.user_id==id, Comment.author_id==uid).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_comments(listing, v=v)

	return render_template("voted_comments.html", next_exists=next_exists, listing=listing, page=page, v=v, standalone=True)


@app.get("/@<username>/upvoted/posts")
@auth_required
def user_upvoted_posts(v, username):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).join(Vote).filter(
			Submission.ghost == False,
			Submission.is_banned == False,
			Submission.deleted_utc == 0,
			Submission.author_id != u.id,
			Vote.user_id == u.id,
			Vote.vote_type == 1
		).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]
	listing = get_posts(listing, v=v)

	return render_template("voted_posts.html", next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/@<username>/upvoted/comments")
@auth_required
def user_upvoted_comments(v, username):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment).join(CommentVote).filter(
			Comment.ghost == False,
			Comment.is_banned == False,
			Comment.deleted_utc == 0,
			Comment.author_id != u.id,
			CommentVote.user_id == u.id,
			CommentVote.vote_type == 1
		).order_by(Comment.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]
	listing = get_comments(listing, v=v)

	return render_template("voted_comments.html", next_exists=next_exists, listing=listing, page=page, v=v, standalone=True)


@app.get("/poorcels")
@auth_required
def poorcels(v):
	users = g.db.query(User).filter_by(poorcel=True).all()

	return render_template("poorcels.html", v=v, users=users)


@app.get("/grassed")
@auth_required
def grassed(v):
	users = g.db.query(User).filter(User.ban_reason.like('grass award used by @%')).all()

	return render_template("grassed.html", v=v, users=users)

@app.get("/agendaposters")
@auth_required
def agendaposters(v):
	users = g.db.query(User).filter(User.agendaposter > 0).order_by(User.username).all()
	return render_template("agendaposters.html", v=v, users=users)


@app.get("/@<username>/upvoters")
@auth_required
def upvoters(v, username):
	id = get_user(username, v=v, include_shadowbanned=False).id
	if not (v.id == id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)

	votes = g.db.query(Vote.user_id, func.count(Vote.user_id)).join(Submission).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==1, Submission.author_id==id).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()

	votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).join(Comment).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==1, Comment.author_id==id).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()

	votes = Counter(dict(votes)) + Counter(dict(votes2))

	total = sum(votes.values())

	users = g.db.query(User).filter(User.id.in_(votes.keys())).all()
	users2 = []
	for user in users: users2.append((user, votes[user.id]))

	users = sorted(users2, key=lambda x: x[1], reverse=True)
	
	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	if total == 1: total=f'{total} upvote received'
	else: total=f'{total} upvotes received'

	return render_template("voters.html", v=v, users=users[:25], pos=pos, name='Up', name2=f'@{username} biggest simps', total=total)



@app.get("/@<username>/downvoters")
@auth_required
def downvoters(v, username):
	id = get_user(username, v=v, include_shadowbanned=False).id
	if not (v.id == id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)

	votes = g.db.query(Vote.user_id, func.count(Vote.user_id)).join(Submission).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==-1, Submission.author_id==id).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()

	votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).join(Comment).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==-1, Comment.author_id==id).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()

	votes = Counter(dict(votes)) + Counter(dict(votes2))

	total = sum(votes.values())

	users = g.db.query(User).filter(User.id.in_(votes.keys())).all()
	users2 = []
	for user in users: users2.append((user, votes[user.id]))

	users = sorted(users2, key=lambda x: x[1], reverse=True)
	
	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	if total == 1: total=f'{total} downvote received'
	else: total=f'{total} downvotes received'

	return render_template("voters.html", v=v, users=users[:25], pos=pos, name='Down', name2=f'@{username} biggest haters', total=total)

@app.get("/@<username>/upvoting")
@auth_required
def upvoting(v, username):
	id = get_user(username, v=v, include_shadowbanned=False).id
	if not (v.id == id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)

	votes = g.db.query(Submission.author_id, func.count(Submission.author_id)).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==1, Vote.user_id==id).group_by(Submission.author_id).order_by(func.count(Submission.author_id).desc()).all()

	votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==1, CommentVote.user_id==id).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()

	votes = Counter(dict(votes)) + Counter(dict(votes2))

	total = sum(votes.values())

	users = g.db.query(User).filter(User.id.in_(votes.keys())).all()
	users2 = []
	for user in users: users2.append((user, votes[user.id]))

	users = sorted(users2, key=lambda x: x[1], reverse=True)
	
	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	if total == 1: total=f'{total} upvote given'
	else: total=f'{total} upvotes given'

	return render_template("voters.html", v=v, users=users[:25], pos=pos, name='Up', name2=f'Who @{username} simps for', total=total)

@app.get("/@<username>/downvoting")
@auth_required
def downvoting(v, username):
	id = get_user(username, v=v, include_shadowbanned=False).id
	if not (v.id == id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)

	votes = g.db.query(Submission.author_id, func.count(Submission.author_id)).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==-1, Vote.user_id==id).group_by(Submission.author_id).order_by(func.count(Submission.author_id).desc()).all()

	votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==-1, CommentVote.user_id==id).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()

	votes = Counter(dict(votes)) + Counter(dict(votes2))

	total = sum(votes.values())

	users = g.db.query(User).filter(User.id.in_(votes.keys())).all()
	users2 = []
	for user in users: users2.append((user, votes[user.id]))

	users = sorted(users2, key=lambda x: x[1], reverse=True)
	
	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	if total == 1: total=f'{total} downvote given'
	else: total=f'{total} downvotes given'

	return render_template("voters.html", v=v, users=users[:25], pos=pos, name='Down', name2=f'Who @{username} hates', total=total)



@app.post("/@<username>/suicide")
@limiter.limit("1/second;5/day")
@limiter.limit("1/second;5/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def suicide(v, username):
	if not FEATURES['USERS_SUICIDE']:
		abort(403)

	user = get_user(username)
	suicide = f"Hi there,\n\nA [concerned user](/id/{v.id}) reached out to us about you.\n\nWhen you're in the middle of something painful, it may feel like you don't have a lot of options. But whatever you're going through, you deserve help and there are people who are here for you.\n\nThere are resources available in your area that are free, confidential, and available 24/7:\n\n- Call, Text, or Chat with Canada's [Crisis Services Canada](https://www.crisisservicescanada.ca/en/)\n- Call, Email, or Visit the UK's [Samaritans](https://www.samaritans.org/)\n- Text CHAT to America's [Crisis Text Line](https://www.crisistextline.org/) at 741741.\nIf you don't see a resource in your area above, the moderators keep a comprehensive list of resources and hotlines for people organized by location. Find Someone Now\n\nIf you think you may be depressed or struggling in another way, don't ignore it or brush it aside. Take yourself and your feelings seriously, and reach out to someone.\n\nIt may not feel like it, but you have options. There are people available to listen to you, and ways to move forward.\n\nYour fellow users care about you and there are people who want to help."
	if not v.shadowbanned:
		send_notification(user.id, suicide)
	return {"message": f"Help message sent to @{user.username}"}


@app.get("/@<username>/coins")
@auth_required
def get_coins(v, username):
	user = get_user(username, v=v, include_shadowbanned=False)
	return {"coins": user.coins}

@app.post("/@<username>/transfer_coins")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def transfer_coins(v, username):
	receiver = get_user(username, v=v, include_shadowbanned=False)

	if receiver.id != v.id:
		amount = request.values.get("amount", "").strip()
		amount = int(amount) if amount.isdigit() else None
		reason = request.values.get("reason", "").strip()

		if amount is None or amount <= 0: return {"error": "Invalid amount of coins."}, 400
		if v.coins < amount: return {"error": "You don't have enough coins."}, 400
		if amount < 100: return {"error": "You have to gift at least 100 coins."}, 400

		if not v.patron and not receiver.patron and not v.alts_patron and not receiver.alts_patron: tax = math.ceil(amount*0.03)
		else: tax = 0

		v.coins -= amount

		if not v.shadowbanned:
			receiver.coins += amount - tax

			log_message = f"@{v.username} has transferred {amount} coins to @{receiver.username}"
			notif_text = f":marseycapitalistmanlet: @{v.username} has gifted you {amount-tax} coins!"

			if reason:
				if len(reason) > 200: return {"error": "Reason is too long, max 200 characters"},400
				notif_text += f"\n\n> {reason}"
				log_message += f"\n\n> {reason}"

			send_repeatable_notification(GIFT_NOTIF_ID, log_message)
			send_repeatable_notification(receiver.id, notif_text)

		g.db.add(receiver)
		g.db.add(v)

		return {"message": f"{amount-tax} coins have been transferred to @{receiver.username}"}, 200

	return {"message": "You can't transfer coins to yourself!"}, 400


@app.post("/@<username>/transfer_bux")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def transfer_bux(v, username):
	receiver = get_user(username, v=v, include_shadowbanned=False)
	
	if receiver.id != v.id:
		amount = request.values.get("amount", "").strip()
		amount = int(amount) if amount.isdigit() else None
		reason = request.values.get("reason", "").strip()

		if not amount or amount < 0: return {"error": "Invalid amount of marseybux."}, 400
		if v.procoins < amount: return {"error": "You don't have enough marseybux"}, 400
		if amount < 100: return {"error": "You have to gift at least 100 marseybux."}, 400

		v.procoins -= amount

		if not v.shadowbanned:
			receiver.procoins += amount

			log_message = f"@{v.username} has transferred {amount} marseybux to @{receiver.username}"
			notif_text = f":marseycapitalistmanlet: @{v.username} has gifted you {amount} marseybux!"

			if reason:
				if len(reason) > 200: return {"error": "Reason is too long, max 200 characters"},400
				notif_text += f"\n\n> {reason}"
				log_message += f"\n\n> {reason}"

			send_repeatable_notification(GIFT_NOTIF_ID, log_message)
			send_repeatable_notification(receiver.id, notif_text)

		g.db.add(receiver)
		g.db.add(v)
		return {"message": f"{amount} marseybux have been transferred to @{receiver.username}"}, 200

	return {"message": "You can't transfer marseybux to yourself!"}, 400


@app.get("/leaderboard")
@auth_required
def leaderboard(v):

	users = g.db.query(User)

	users1 = users.order_by(User.coins.desc()).limit(25).all()
	if v in users1:
		pos1 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.coins.desc()).label("rank")).subquery()
		pos1 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	users2 = users.order_by(User.stored_subscriber_count.desc()).limit(25).all()
	if v in users2:
		pos2 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.stored_subscriber_count.desc()).label("rank")).subquery()
		pos2 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	users3 = users.order_by(User.post_count.desc()).limit(25).all()
	if v in users3:
		pos3 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.post_count.desc()).label("rank")).subquery()
		pos3 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	users4 = users.order_by(User.comment_count.desc()).limit(25).all()
	if v in users4:
		pos4 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.comment_count.desc()).label("rank")).subquery()
		pos4 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	users5 = users.order_by(User.received_award_count.desc()).limit(25).all()
	if v in users5:
		pos5 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.received_award_count.desc()).label("rank")).subquery()
		pos5 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	users7 = users.order_by(User.coins_spent.desc()).limit(25).all()
	if v in users7:
		pos7 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.coins_spent.desc()).label("rank")).subquery()
		pos7 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	# Received Downvotes
	dv_stmt = text("""
		SELECT
			u.id,
			(coalesce(cv.count, 0) + coalesce(pv.count, 0)) as downvotes
		FROM
			users u
		LEFT OUTER JOIN
			(SELECT c.author_id, COUNT(*) FROM commentvotes v
				JOIN comments c ON v.comment_id = c.id WHERE v.vote_type = -1
				GROUP BY c.author_id) AS cv
			ON cv.author_id = u.id
		LEFT OUTER JOIN
			(SELECT p.author_id, COUNT(*) FROM votes v
				JOIN submissions p ON v.submission_id = p.id WHERE v.vote_type = -1
				GROUP BY p.author_id) AS pv
			ON pv.author_id = u.id
		ORDER BY downvotes DESC;
	""")
	dv_result = g.db.execute(dv_stmt).fetchall() or [(None,None)]
	users9_1, users9_2 = zip(*dv_result[:25])

	users9_accs = g.db.query(User).filter(User.id.in_(users9_1)).all()
	users9_accs = sorted(users9_accs, key=lambda x: users9_1.index(x.id))
	users9_accs = zip(users9_accs, users9_2)
	try:
		pos9 = [x[0] for x in dv_result].index(v.id)
		pos9 = (pos9+1, dv_result[pos9][1])
	except: pos9 = (len(dv_result)+1, 0)

	users10 = users.order_by(User.truecoins.desc()).limit(25).all()
	if v in users10:
		pos10 = None
	else:
		sq = g.db.query(User.id, func.rank().over(order_by=User.truecoins.desc()).label("rank")).subquery()
		pos10 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	sq = g.db.query(Badge.user_id, func.count(Badge.user_id).label("count"), func.rank().over(order_by=func.count(Badge.user_id).desc()).label("rank")).group_by(Badge.user_id).subquery()
	users11 = g.db.query(User, sq.c.count).join(sq, User.id==sq.c.user_id).order_by(sq.c.count.desc())
	pos11 = g.db.query(User.id, sq.c.rank, sq.c.count).join(sq, User.id==sq.c.user_id).filter(User.id == v.id).one_or_none()
	if pos11: pos11 = (pos11[1],pos11[2])
	else: pos11 = (users11.count()+1, 0)
	users11 = users11.limit(25).all()

	if SITE_NAME == 'rDrama':
		sq = g.db.query(Marsey.author_id, func.count(Marsey.author_id).label("count"), func.rank().over(order_by=func.count(Marsey.author_id).desc()).label("rank")).filter(Marsey.submitter_id==None).group_by(Marsey.author_id).subquery()
		users12 = g.db.query(User, sq.c.count).join(sq, User.id==sq.c.author_id).order_by(sq.c.count.desc())
		pos12 = g.db.query(User.id, sq.c.rank, sq.c.count).join(sq, User.id==sq.c.author_id).filter(User.id == v.id).one_or_none()
		if pos12: pos12 = (pos12[1],pos12[2])
		else: pos12 = (users12.count()+1, 0)
		users12 = users12.limit(25).all()
	else:
		users12 = None
		pos12 = None

	# winnings_sq = g.db.query(Casino_Game.user_id, func.sum(Casino_Game.winnings)).group_by(Casino_Game.user_id).subquery()
	# users14 = g.db.query(User).join(winnings_sq, winnings_sq.c.user_id == User.id).order_by(winnings_sq.c.sum.desc()).limit(25).all()
	# if v in users14:
	# 	pos14 = None
	# else:
	# 	sq = g.db.query(User.id, func.rank().over(order_by=winnings_sq.c.sum.desc()).label("rank")).join(winnings_sq, winnings_sq.c.user_id == User.id).subquery()
	# 	pos14 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	# users15 = g.db.query(User).join(winnings_sq, winnings_sq.c.user_id == User.id).order_by(winnings_sq.c.sum.asc()).limit(25).all()
	# if v in users15:
	# 	pos15 = None
	# else:
	# 	sq = g.db.query(User.id, func.rank().over(order_by=winnings_sq.c.sum.asc()).label("rank")).join(winnings_sq, winnings_sq.c.user_id == User.id).subquery()
	# 	pos15 = g.db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]

	sq = g.db.query(UserBlock.target_id, func.count(UserBlock.target_id).label("count")).group_by(UserBlock.target_id).subquery()
	users16 = g.db.query(User, sq.c.count).join(User, User.id == sq.c.target_id).order_by(sq.c.count.desc())
	sq = g.db.query(UserBlock.target_id, func.count(UserBlock.target_id).label("count"), func.rank().over(order_by=func.count(UserBlock.target_id).desc()).label("rank")).group_by(UserBlock.target_id).subquery()
	pos16 = g.db.query(sq.c.rank, sq.c.count).join(User, User.id == sq.c.target_id).filter(sq.c.target_id == v.id).limit(1).one_or_none()
	if not pos16: pos16 = (users16.count()+1, 0)
	users16 = users16.limit(25).all()

	users17 = g.db.query(User, func.count(User.owned_hats)).join(User.owned_hats).group_by(User).order_by(func.count(User.owned_hats).desc())
	sq = g.db.query(User.id, func.count(User.owned_hats).label("count"), func.rank().over(order_by=func.count(User.owned_hats).desc()).label("rank")).join(User.owned_hats).group_by(User).subquery()
	pos17 = g.db.query(sq.c.rank, sq.c.count).filter(sq.c.id == v.id).limit(1).one_or_none()
	if not pos17: pos17 = (users17.count()+1, 0)
	users17 = users17.limit(25).all()

	users18 = g.db.query(User, func.count(User.designed_hats)).join(User.designed_hats).group_by(User).order_by(func.count(User.designed_hats).desc())
	sq = g.db.query(User.id, func.count(User.designed_hats).label("count"), func.rank().over(order_by=func.count(User.designed_hats).desc()).label("rank")).join(User.designed_hats).group_by(User).subquery()
	pos18 = g.db.query(sq.c.rank, sq.c.count).filter(sq.c.id == v.id).limit(1).one_or_none()
	if not pos18: pos18 = (users18.count()+1, 0)
	users18 = users18.limit(25).all()

	return render_template("leaderboard.html", v=v, users1=users1, pos1=pos1, users2=users2, pos2=pos2, 
		users3=users3, pos3=pos3, users4=users4, pos4=pos4, users5=users5, pos5=pos5, 
		users7=users7, pos7=pos7, users9=users9_accs, pos9=pos9, 
		users10=users10, pos10=pos10, users11=users11, pos11=pos11, users12=users12, pos12=pos12, users16=users16, pos16=pos16, users17=users17, pos17=pos17, users18=users18, pos18=pos18)

@app.get("/<id>/css")
def get_css(id):
	try: id = int(id)
	except: abort(404)

	css = g.db.query(User.css).filter_by(id=id).one_or_none()
	if not css: abort(404)

	resp = make_response(css[0] or "")
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/<id>/profilecss")
def get_profilecss(id):
	try: id = int(id)
	except: abort(404)

	css = g.db.query(User.profilecss).filter_by(id=id).one_or_none()
	if not css: abort(404)

	resp = make_response(css[0] or "")
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/@<username>/song")
def usersong(username):
	user = get_user(username)
	if user.song: return redirect(f"/song/{user.song}.mp3")
	else: abort(404)

@app.get("/song/<song>")
@app.get("/static/song/<song>")
def song(song):
	resp = make_response(send_from_directory('/songs', song))
	resp.headers.remove("Cache-Control")
	resp.headers.add("Cache-Control", "public, max-age=3153600")
	return resp

@app.post("/subscribe/<post_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def subscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, submission_id=post_id).one_or_none()
	if not existing:
		new_sub = Subscription(user_id=v.id, submission_id=post_id)
		g.db.add(new_sub)
	return {"message": "Subscribed to post successfully!"}
	
@app.post("/unsubscribe/<post_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def unsubscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, submission_id=post_id).one_or_none()
	if existing:
		g.db.delete(existing)
	return {"message": "Unsubscribed from post successfully!"}

@app.post("/@<username>/message")
@limiter.limit("1/second;10/minute;20/hour;50/day")
@limiter.limit("1/second;10/minute;20/hour;50/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def message2(v, username):
	user = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		return {"error": "You're blocking this user."}, 403

	if v.admin_level <= 1 and hasattr(user, 'is_blocked') and user.is_blocked:
		return {"error": "This user is blocking you."}, 403

	message = request.values.get("message", "").strip()[:10000].strip()

	if not message: return {"error": "Message is empty!"}, 400

	if 'linkedin.com' in message: return {"error": "This domain 'linkedin.com' is banned."}, 403

	body_html = sanitize(message)

	if not (SITE == 'rdrama.net' and user.id == 12732):
		existing = g.db.query(Comment.id).filter(Comment.author_id == v.id,
																Comment.sentto == user.id,
																Comment.body_html == body_html,
																).first()

		if existing: return {"error": "Message already exists."}, 403

	c = Comment(author_id=v.id,
						parent_submission=None,
						level=1,
						sentto=user.id,
						body_html=body_html
						)
	g.db.add(c)

	g.db.flush()

	if blackjack and any(i in c.body_html.lower() for i in blackjack.split()):
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = 'Blackjack'
		g.db.add(v)
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=CARP_ID).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=CARP_ID)
			g.db.add(notif)
			g.db.flush()

	c.top_comment_id = c.id

	if user.id not in bots:
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user.id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user.id)
			g.db.add(notif)


	if PUSHER_ID != 'blahblahblah' and not v.shadowbanned:
		interests = f'{SITE}{user.id}'

		title = f'New message from @{username}'

		if len(message) > 500: notifbody = message[:500] + '...'
		else: notifbody = message

		url = f'{SITE_FULL}/notifications/messages'

		gevent.spawn(pusher_thread, interests, title, notifbody, url)

	return {"message": "Message sent!"}


@app.post("/reply")
@limiter.limit("1/second;6/minute;50/hour;200/day")
@limiter.limit("1/second;6/minute;50/hour;200/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def messagereply(v):
	body = request.values.get("body", "").strip().replace('‎','')
	body = body.replace('\r\n', '\n')[:10000]

	if not body and not request.files.get("file"): return {"error": "Message is empty!"}, 400

	if 'linkedin.com' in body: return {"error": "this domain 'linkedin.com' is banned"}, 400

	id = int(request.values.get("parent_id"))
	parent = get_comment(id, v=v)
	user_id = parent.author.id

	if v.is_suspended_permanently and parent.sentto != 2:
		return {"error": "You are permabanned and may not reply to messages."}, 400
	elif v.is_muted and parent.sentto == 2:
		return {"error": "You are forbidden from replying to modmail."}, 400

	if parent.sentto == 2: user_id = None
	elif v.id == user_id: user_id = parent.sentto

	if parent.sentto == 2:
		body += process_files()

	body = body.strip()

	body_html = sanitize(body)

	c = Comment(author_id=v.id,
							parent_submission=None,
							parent_comment_id=id,
							top_comment_id=parent.top_comment_id,
							level=parent.level + 1,
							sentto=user_id,
							body_html=body_html,
							)
	g.db.add(c)
	g.db.flush()

	if blackjack and any(i in c.body_html.lower() for i in blackjack.split()):
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = 'Blackjack'
		g.db.add(v)
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=CARP_ID).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=CARP_ID)
			g.db.add(notif)
			g.db.flush()

	if user_id and user_id not in (v.id, 2, bots):
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user_id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user_id)
			g.db.add(notif)

		if PUSHER_ID != 'blahblahblah' and not v.shadowbanned:
			interests = f'{SITE}{user_id}'

			title = f'New message from @{v.username}'

			if len(body) > 500: notifbody = body[:500] + '...'
			else: notifbody = body

			url = f'{SITE_FULL}/notifications/messages'

			gevent.spawn(pusher_thread, interests, title, notifbody, url)



	if c.top_comment.sentto == 2:
		admins = g.db.query(User.id).filter(User.admin_level > 2, User.id != v.id)
		if SITE == 'watchpeopledie.co':
			admins = admins.filter(User.id != AEVANN_ID)

		admins = [x[0] for x in admins.all()]

		if parent.author.id not in admins:
			admins.append(parent.author.id)

		for admin in admins:
			notif = Notification(comment_id=c.id, user_id=admin)
			g.db.add(notif)

		ids = [c.top_comment.id] + [x.id for x in c.top_comment.replies(None)]
		notifications = g.db.query(Notification).filter(Notification.comment_id.in_(ids), Notification.user_id.in_(admins))
		for n in notifications:
			g.db.delete(n)


	return {"comment": render_template("comments.html", v=v, comments=[c])}

@app.get("/2faqr/<secret>")
@auth_required
def mfa_qr(secret, v):
	x = pyotp.TOTP(secret)
	qr = qrcode.QRCode(
		error_correction=qrcode.constants.ERROR_CORRECT_L
	)
	qr.add_data(x.provisioning_uri(v.username, issuer_name=SITE_NAME))
	img = qr.make_image(fill_color="#000000", back_color="white")

	mem = io.BytesIO()

	img.save(mem, format="PNG")
	mem.seek(0, 0)

	return send_file(mem, mimetype="image/png", as_attachment=False)


@app.get("/is_available/<name>")
@limiter.limit("100/day")
def is_available(name):

	name=name.strip()

	if len(name)<3 or len(name)>25:
		return {name:False}
		
	name2 = name.replace('\\', '').replace('_','\_').replace('%','')

	x = g.db.query(User).filter(
		or_(
			User.username.ilike(name2),
			User.original_username.ilike(name2)
			)
		).one_or_none()

	if x:
		return {name: False}
	else:
		return {name: True}

@app.get("/id/<id>")
def user_id(id):
	user = get_account(id)
	return redirect(user.url)
		
@app.get("/u/<username>")
@auth_required
def redditor_moment_redirect(username, v):
	return redirect(f"/@{username}")

@app.get("/@<username>/followers")
@auth_required
def followers(username, v):
	u = get_user(username, v=v, include_shadowbanned=False)
	if u.id == CARP_ID and SITE == 'watchpeopledie.co': abort(403)

	if not (v.id == u.id or v.admin_level >= PERMS['USER_FOLLOWS_VISIBLE']):
		abort(403)

	users = g.db.query(Follow, User).join(Follow, Follow.target_id == u.id) \
		.filter(Follow.user_id == User.id) \
		.order_by(Follow.created_utc).all()
	return render_template("followers.html", v=v, u=u, users=users)

@app.get("/@<username>/blockers")
@auth_required
def blockers(username, v):
	u = get_user(username, v=v, include_shadowbanned=False)

	users = g.db.query(UserBlock, User).join(UserBlock, UserBlock.target_id == u.id) \
		.filter(UserBlock.user_id == User.id) \
		.order_by(UserBlock.created_utc).all()
	return render_template("blockers.html", v=v, u=u, users=users)

@app.get("/@<username>/following")
@auth_required
def following(username, v):
	u = get_user(username, v=v, include_shadowbanned=False)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_FOLLOWS_VISIBLE']):
		abort(403)

	users = g.db.query(User).join(Follow, Follow.user_id == u.id) \
		.filter(Follow.target_id == User.id) \
		.order_by(Follow.created_utc).all()
	return render_template("following.html", v=v, u=u, users=users)

@app.get("/views")
@auth_required
def visitors(v):
	if not v.viewers_recorded:
		return render_template("errors/patron.html", v=v)
	viewers=sorted(v.viewers, key = lambda x: x.last_view_utc, reverse=True)
	return render_template("viewers.html", v=v, viewers=viewers)


@app.get("/@<username>")
@app.get("/@<username>.json")
@app.get("/logged_out/@<username>")
@auth_desired_with_logingate
def u_username(username, v=None):

	u = get_user(username, v=v, include_blocks=True, include_shadowbanned=False, rendered=True)

	if v and username == v.username:
		is_following = False
	else:
		is_following = (v and u.has_follower(v))


	if username != u.username:
		return redirect(SITE_FULL + request.full_path.replace(username, u.username))

	if u.reserved:
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": f"This username is reserved for: {u.reserved}"}, 418

		return render_template("userpage_reserved.html", u=u, v=v)

	if v and v.id not in (u.id, DAD_ID) and u.viewers_recorded:
		g.db.flush()
		view = g.db.query(ViewerRelationship).filter_by(viewer_id=v.id, user_id=u.id).one_or_none()

		if view: view.last_view_utc = int(time.time())
		else: view = ViewerRelationship(viewer_id=v.id, user_id=u.id)

		g.db.add(view)
		g.db.commit()

		
	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)):
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": "This userpage is private"}, 403

		return render_template("userpage_private.html", u=u, v=v)

	
	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": f"You are blocking @{u.username}."}, 403

		return render_template("userpage_blocking.html", u=u, v=v)


	sort = request.values.get("sort", "new")
	t = request.values.get("t", "all")
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	ids = u.userpagelisting(site=SITE, v=v, page=page, sort=sort, t=t)

	next_exists = (len(ids) > 25)
	ids = ids[:25]

	if page == 1:
		sticky = []
		sticky = g.db.query(Submission).filter_by(is_pinned=True, author_id=u.id).all()
		if sticky:
			for p in sticky:
				ids = [p.id] + ids

	listing = get_posts(ids, v=v)

	if u.unban_utc:
		if request.headers.get("Authorization") or request.path.endswith(".json"):
			return {"data": [x.json for x in listing]}
		
		return render_template("userpage.html",
												unban=u.unban_string,
												u=u,
												v=v,
												listing=listing,
												page=page,
												sort=sort,
												t=t,
												next_exists=next_exists,
												is_following=is_following)



	if request.headers.get("Authorization") or request.path.endswith(".json"):
		return {"data": [x.json for x in listing]}
	
	return render_template("userpage.html",
									u=u,
									v=v,
									listing=listing,
									page=page,
									sort=sort,
									t=t,
									next_exists=next_exists,
									is_following=is_following)


@app.get("/@<username>/comments")
@app.get("/@<username>/comments.json")
@app.get("/logged_out/@<username>/comments")
@auth_desired_with_logingate
def u_username_comments(username, v=None):

	user = get_user(username, v=v, include_blocks=True, include_shadowbanned=False, rendered=True)

	if v and username == v.username:
		is_following = False
	else:
		is_following = (v and user.has_follower(v))

	if username != user.username:
		return redirect(f'/@{user.username}/comments')

	u = user

	if u.reserved:
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": f"This username is reserved for: {u.reserved}"}, 418
		return render_template("userpage_reserved.html", u=u, v=v)


	if u.is_private and (not v or (v.id != u.id and v.admin_level < 2 and not v.eye)):
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": "This userpage is private"}, 403
		return render_template("userpage_private.html", u=u, v=v)

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if request.headers.get("Authorization") or request.headers.get("xhr") or request.path.endswith(".json"):
			return {"error": f"You are blocking @{u.username}."}, 403
		return render_template("userpage_blocking.html", u=u, v=v)

	try: page = max(int(request.values.get("page", "1")), 1)
	except: page = 1
	
	sort=request.values.get("sort","new")
	t=request.values.get("t","all")

	comment_post_author = aliased(User)
	comments = g.db.query(Comment.id) \
				.join(Comment.post) \
				.join(comment_post_author, Submission.author) \
				.filter(
					Comment.author_id == u.id,
					Comment.parent_submission != None
				)

	if not v or (v.id != u.id and v.admin_level < 2):
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			comment_post_author.shadowbanned == None,
			Comment.deleted_utc == 0
		)

	comments = apply_time_filter(t, comments, Comment)

	comments = sort_comments(sort, comments)

	comments = comments.offset(25 * (page - 1)).limit(26).all()
	ids = [x.id for x in comments]

	next_exists = (len(ids) > 25)
	ids = ids[:25]

	listing = get_comments(ids, v=v)

	if request.headers.get("Authorization") or request.path.endswith(".json"):
		return {"data": [c.json for c in listing]}
	
	return render_template("userpage_comments.html", u=user, v=v, listing=listing, page=page, sort=sort, t=t,next_exists=next_exists, is_following=is_following, standalone=True)


@app.get("/@<username>/info")
@auth_required
def u_username_info(username, v=None):

	user=get_user(username, v=v, include_blocks=True, include_shadowbanned=False)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		return {"error": "You're blocking this user."}, 401
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		return {"error": "This user is blocking you."}, 403

	return user.json

@app.get("/<id>/info")
@auth_required
def u_user_id_info(id, v=None):

	user=get_account(id, v=v, include_blocks=True, include_shadowbanned=False)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		return {"error": "You're blocking this user."}, 401
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		return {"error": "This user is blocking you."}, 403

	return user.json

@app.post("/follow/<username>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def follow_user(username, v):

	target = get_user(username, v=v, include_shadowbanned=False)

	if target.id==v.id:
		return {"error": "You can't follow yourself!"}, 400

	if target.is_nofollow:
		return {"error": "This user has disallowed other users from following them!"}, 403

	if g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none():
		return {"message": f"@{target.username} has been followed!"}

	new_follow = Follow(user_id=v.id, target_id=target.id)
	g.db.add(new_follow)

	g.db.flush()
	target.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=target.id).count()
	g.db.add(target)

	if not v.shadowbanned:
		send_notification(target.id, f"@{v.username} has followed you!")


	return {"message": f"@{target.username} has been followed!"}

@app.post("/unfollow/<username>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def unfollow_user(username, v):

	target = get_user(username)

	if target.fish:
		if not v.shadowbanned:
			send_notification(target.id, f"@{v.username} has tried to unfollow you and failed because of your fish award!")
		return {"error": "You can't unfollow this user!"}, 400

	follow = g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none()

	if follow:
		g.db.delete(follow)
		
		g.db.flush()
		target.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=target.id).count()
		g.db.add(target)

		if not v.shadowbanned:
			send_notification(target.id, f"@{v.username} has unfollowed you!")


	return {"message": f"@{target.username} has been unfollowed!"}

@app.post("/remove_follow/<username>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def remove_follow(username, v):
	target = get_user(username)

	follow = g.db.query(Follow).filter_by(user_id=target.id, target_id=v.id).one_or_none()

	if not follow: return {"message": f"@{target.username} has been removed as a follower!"}

	g.db.delete(follow)
	
	g.db.flush()
	v.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=v.id).count()
	g.db.add(v)

	send_repeatable_notification(target.id, f"@{v.username} has removed your follow!")


	return {"message": f"@{target.username} has been removed as a follower!"}

@app.get("/pp/<id>")
@app.get("/uid/<id>/pic")
@app.get("/uid/<id>/pic/profile")
@app.get("/logged_out/pp/<id>")
@app.get("/logged_out/uid/<id>/pic")
@app.get("/logged_out/uid/<id>/pic/profile")
@cache.memoize(timeout=86400)
@limiter.exempt
def user_profile_uid(id):
	try: id = int(id)
	except:
		try: id = int(id, 36)
		except: abort(404)

	x=get_account(id)
	return redirect(x.profile_url)

@app.get("/@<username>/pic")
@cache.memoize(timeout=86400)
@limiter.exempt
def user_profile_name(username):
	x = get_user(username)
	return redirect(x.profile_url)

@app.get("/@<username>/saved/posts")
@auth_required
def saved_posts(v, username):

	page=int(request.values.get("page",1))

	ids = [x[0] for x in g.db.query(SaveRelationship.submission_id).join(SaveRelationship.post).filter(SaveRelationship.user_id == v.id).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()]

	next_exists=len(ids)>25

	ids=ids[:25]

	listing = get_posts(ids, v=v)

	if request.headers.get("Authorization"): return {"data": [x.json for x in listing]}
	return render_template("userpage.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											)


@app.get("/@<username>/saved/comments")
@auth_required
def saved_comments(v, username):

	page=int(request.values.get("page",1))

	ids = [x[0] for x in g.db.query(CommentSaveRelationship.comment_id).join(CommentSaveRelationship.comment).filter(CommentSaveRelationship.user_id == v.id).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()]

	next_exists=len(ids) > 25

	ids=ids[:25]

	listing = get_comments(ids, v=v)

	if request.headers.get("Authorization"): return {"data": [x.json for x in listing]}
	return render_template("userpage_comments.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											standalone=True)

@app.get("/@<username>/subscribed/posts")
@auth_required
def subscribed_posts(v, username):

	page=int(request.values.get("page",1))

	ids = [x[0] for x in g.db.query(Subscription.submission_id).join(Subscription.post).filter(Subscription.user_id == v.id).order_by(Submission.created_utc.desc()).offset(25 * (page - 1)).limit(26).all()]

	next_exists=len(ids)>25

	ids=ids[:25]

	listing = get_posts(ids, v=v)

	if request.headers.get("Authorization"): return {"data": [x.json for x in listing]}
	return render_template("userpage.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											)



@app.post("/fp/<fp>")
@auth_required
def fp(v, fp):
	v.fp = fp
	users = g.db.query(User).filter(User.fp == fp, User.id != v.id).all()
	if users: print(f'{v.username}: fp', flush=True)
	if v.email and v.is_activated:
		alts = g.db.query(User).filter(User.email == v.email, User.is_activated, User.id != v.id).all()
		if alts:
			print(f'{v.username}: email', flush=True)
			users += alts
	for u in users:
		li = [v.id, u.id]
		existing = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).one_or_none()
		if existing: continue
		new_alt = Alt(user1=v.id, user2=u.id)
		g.db.add(new_alt)
		g.db.flush()
		print(v.username + ' + ' + u.username, flush=True)
		check_for_alts(v)
	g.db.add(v)
	return '', 204

@app.get("/toggle_pins/<sort>")
def toggle_pins(sort):
	if sort == 'hot': default = True
	else: default = False

	pins = session.get(sort, default)
	session[sort] = not pins

	if is_site_url(request.referrer):
		return redirect(request.referrer)
	return redirect('/')


@app.get("/badge_owners/<bid>")
@auth_required
def bid_list(v, bid):

	try: bid = int(bid)
	except: abort(400)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(User).join(User.badges).filter(Badge.badge_id==bid).offset(25 * (page - 1)).limit(26).all()

	next_exists = (len(users) > 25)
	users = users[:25]

	return render_template("user_cards.html",
						v=v,
						users=users,
						next_exists=next_exists,
						page=page,
						)


@app.post("/kofi")
def kofi():
	data = json.loads(request.values['data'])
	verification_token = data['verification_token']
	if verification_token != KOFI_TOKEN: abort(400)

	id = data['kofi_transaction_id']
	created_utc = int(time.mktime(time.strptime(data['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
	type = data['type']
	amount = int(float(data['amount']))
	email = data['email']

	transaction = Transaction(
		id=id,
		created_utc=created_utc,
		type=type,
		amount=amount,
		email=email
	)

	g.db.add(transaction)
	return ''

kofi_tiers={
	5: 1,
	10: 2,
	20: 3,
	50: 4,
	100: 5
	}

@app.post("/settings/kofi")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def settings_kofi(v):
	if not (v.email and v.is_activated):
		return {"error": f"You must have a verified email to verify {patron} status and claim your rewards!"}, 400

	transaction = g.db.query(Transaction).filter_by(email=v.email).order_by(Transaction.created_utc.desc()).first()

	if not transaction:
		return {"error": "Email not found"}, 404

	if transaction.claimed:
		return {"error": f"{patron} rewards already claimed"}, 400

	tier = kofi_tiers[transaction.amount]

	v.patron = tier
	if v.discord_id: add_role(v, f"{tier}")

	procoins = procoins_li[tier]

	v.procoins += procoins
	send_repeatable_notification(v.id, f"You have received {procoins} Marseybux! You can use them to buy awards in the [shop](/shop).")

	g.db.add(v)

	badge_grant(badge_id=20+tier, user=v)

	transaction.claimed = True

	g.db.add(transaction)

	return {"message": f"{patron} rewards claimed!"}
