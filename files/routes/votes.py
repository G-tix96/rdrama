from files.helpers.wrappers import *
from files.helpers.get import *
from files.helpers.const import *
from files.classes import *
from flask import *
from files.__main__ import app, limiter, cache

@app.get("/votes/<link>")
@admin_level_required(PERMS['VOTES_VISIBLE'])
def vote_info_get(v, link):
	try:
		if "p_" in link: thing = get_post(int(link.split("p_")[1]), v=v)
		elif "c_" in link: thing = get_comment(int(link.split("c_")[1]), v=v)
		else: abort(400)
	except: abort(400)

	if thing.ghost and v.id != AEVANN_ID: abort(403)

	if isinstance(thing, Submission):
		if thing.author.shadowbanned and not (v and v.admin_level):
			thing_id = g.db.query(Submission.id).filter_by(upvotes=thing.upvotes, downvotes=thing.downvotes).order_by(Submission.id).first()[0]
		else: thing_id = thing.id

		ups = g.db.query(Vote).filter_by(submission_id=thing_id, vote_type=1).order_by(Vote.created_utc).all()

		downs = g.db.query(Vote).filter_by(submission_id=thing_id, vote_type=-1).order_by(Vote.created_utc).all()

	elif isinstance(thing, Comment):
		if thing.author.shadowbanned and not (v and v.admin_level):
			thing_id = g.db.query(Comment.id).filter_by(upvotes=thing.upvotes, downvotes=thing.downvotes).order_by(Comment.id).first()[0]
		else: thing_id = thing.id

		ups = g.db.query(CommentVote).filter_by(comment_id=thing_id, vote_type=1).order_by(CommentVote.created_utc).all()

		downs = g.db.query(CommentVote).filter_by(comment_id=thing_id, vote_type=-1 ).order_by(CommentVote.created_utc).all()

	else: abort(400)

	return render_template("votes.html",
						v=v,
						thing=thing,
						ups=ups,
						downs=downs)

def vote_post_comment(target_id, new, v, cls, vote_cls):
	if new == "-1" and DISABLE_DOWNVOTES: abort(403)
	if new not in ["-1", "0", "1"]: abort(400)
	if request.headers.get("Authorization") and v.id != BBBB_ID: abort(403)
	new = int(new)
	target = None
	if cls == Submission:
		target = get_post(target_id)
	elif cls == Comment:
		target = get_comment(target_id)
	else:
		abort(404)

	coin_delta = 1
	if v.id == target.author.id:
		coin_delta = 0

	coin_mult = 1

	g.db.flush()
	existing = g.db.query(vote_cls).filter_by(user_id=v.id)
	if vote_cls == Vote:
		existing = existing.filter_by(submission_id=target.id)
	elif vote_cls == CommentVote:
		existing = existing.filter_by(comment_id=target.id)
	else:
		abort(400)
	existing = existing.one_or_none()
	
	if DOUBLE_XP_ENABLED > 0:
		if not existing and int(time.time()) > DOUBLE_XP_ENABLED:
			coin_mult = 2
		elif existing and existing.created_utc > DOUBLE_XP_ENABLED:
			coin_mult = 2

	if existing and existing.vote_type == new: return "", 204
	if existing:
		if existing.vote_type == 0 and new != 0:
			target.author.coins += coin_delta * coin_mult
			target.author.truecoins += coin_delta
			g.db.add(target.author)
			existing.vote_type = new
			g.db.add(existing)
		elif existing.vote_type != 0 and new == 0:
			target.author.charge_account('coins', coin_delta * coin_mult)
			target.author.truecoins -= coin_delta
			g.db.add(target.author)
			g.db.delete(existing)
		else:
			existing.vote_type = new
			g.db.add(existing)
	elif new != 0:
		target.author.coins += coin_delta * coin_mult
		target.author.truecoins += coin_delta
		g.db.add(target.author)

		real = new != 1 or v.is_votes_real
		vote = None
		if vote_cls == Vote:
			vote = Vote(user_id=v.id,
						vote_type=new,
						submission_id=target_id,
						app_id=v.client.application.id if v.client else None,
						real = real
			)
		elif vote_cls == CommentVote:		
			vote = CommentVote(user_id=v.id,
						vote_type=new,
						comment_id=target_id,
						app_id=v.client.application.id if v.client else None,
						real=real
			)
		g.db.add(vote)
	g.db.flush()

	# this is hacky but it works, we should probably do better later
	def get_vote_count(dir, real_instead_of_dir):
		votes = g.db.query(vote_cls)
		if real_instead_of_dir:
			votes = votes.filter_by(real=True)
		else:
			votes = votes.filter_by(vote_type=dir)

		if vote_cls == Vote:
			votes = votes.filter_by(submission_id=target.id)
		elif vote_cls == CommentVote:
			votes = votes.filter_by(comment_id=target.id)
		else:
			return 0
		return votes.count()

	target.upvotes = get_vote_count(1, False)
	target.downvotes = get_vote_count(-1, False)
	target.realupvotes = get_vote_count(0, True) # first arg is ignored here

	if target.author.progressivestack or (cls == Submission and (target.sub in ('space', 'istory', 'dinos') or target.domain.endswith('.win'))):
		target.realupvotes *= 2
	g.db.add(target)
	return "", 204

@app.post("/vote/post/<post_id>/<new>")
@limiter.limit("5/second;60/minute;1000/hour;2000/day")
@limiter.limit("5/second;60/minute;1000/hour;2000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def vote_post(post_id, new, v):
	return vote_post_comment(post_id, new, v, Submission, Vote)

@app.post("/vote/comment/<comment_id>/<new>")
@limiter.limit("5/second;60/minute;1000/hour;2000/day")
@limiter.limit("5/second;60/minute;1000/hour;2000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def vote_comment(comment_id, new, v):
	return vote_post_comment(comment_id, new, v, Comment, CommentVote)
