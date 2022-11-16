from files.classes import *
from files.helpers.const import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app, limiter


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
		if thing.author.shadowbanned and not (v and v.admin_level >= PERMS['USER_SHADOWBAN']):
			thing_id = g.db.query(Submission.id).filter_by(upvotes=thing.upvotes, downvotes=thing.downvotes).order_by(Submission.id).first()[0]
		else: thing_id = thing.id

		ups = g.db.query(Vote).filter_by(submission_id=thing_id, vote_type=1).order_by(Vote.created_utc).all()
		downs = g.db.query(Vote).filter_by(submission_id=thing_id, vote_type=-1).order_by(Vote.created_utc).all()

	elif isinstance(thing, Comment):
		if thing.author.shadowbanned and not (v and v.admin_level >= PERMS['USER_SHADOWBAN']):
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
	if v.client and v.id not in PRIVILEGED_USER_BOTS: abort(403)
	new = int(new)
	target = None
	if cls == Submission:
		target = get_post(target_id)
	elif cls == Comment:
		target = get_comment(target_id)
		if not target.post: abort(404)
	else:
		abort(404)

	if target.author.shadowbanned and not v.can_see_shadowbanned:
		abort(404)

	coin_delta = 1
	if v.id == target.author.id:
		coin_delta = 0

	if target.author.id in v.alt_ids or v.id in target.author.alt_ids:
		coin_delta = -1

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
	
	if DOUBLE_XP_ENABLED > 0 and int(time.time()) > DOUBLE_XP_ENABLED:
		coin_mult = 2
	coin_value = coin_delta * coin_mult

	if existing and existing.vote_type == new: return "", 204
	if existing:
		if existing.vote_type == 0 and new != 0:
			target.author.coins += coin_value
			target.author.truescore += coin_delta
			g.db.add(target.author)
			existing.vote_type = new
			existing.coins = coin_value
			g.db.add(existing)
		elif existing.vote_type != 0 and new == 0:
			target.author.charge_account('coins', existing.coins, should_check_balance=False)
			target.author.truescore -= coin_delta
			g.db.add(target.author)
			g.db.delete(existing)
		else:
			existing.vote_type = new
			g.db.add(existing)
	elif new != 0:
		target.author.coins += coin_value
		target.author.truescore += coin_delta
		g.db.add(target.author)

		real = new != 1 or v.is_votes_real
		vote = None
		if vote_cls == Vote:
			vote = Vote(user_id=v.id,
						vote_type=new,
						submission_id=target_id,
						app_id=v.client.application.id if v.client else None,
						real=real,
						coins=coin_value
			)
		elif vote_cls == CommentVote:		
			vote = CommentVote(user_id=v.id,
						vote_type=new,
						comment_id=target_id,
						app_id=v.client.application.id if v.client else None,
						real=real,
						coins=coin_value
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

	if SITE_NAME == 'rDrama':
		target.realupvotes = get_vote_count(0, True) # first arg is ignored here

		mul = 1
		if target.author.progressivestack or target.author.id in BOOSTED_USERS:
			mul = 2
		elif cls == Submission:
			if target.domain.endswith('.win') or target.domain in BOOSTED_SITES or target.sub in BOOSTED_HOLES:
				mul = 2
			elif target.sub and target.sub not in ('space','istory','dino','slackernews'):
				mul = 0.7
			elif not target.sub and target.body_html:
				x = target.body_html.count('" target="_blank" rel="nofollow noopener">')
				x += target.body_html.count('<a href="/images/')
				mul = 1 + x/20

		mul = min(mul, 2)
		target.realupvotes *= mul

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
