from files.classes import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app


@app.post("/vote/post/option/<option_id>")
@is_not_permabanned
def vote_option(option_id, v):
	try:
		option_id = int(option_id)
	except:
		abort(404)
	option = g.db.get(SubmissionOption, option_id)
	if not option: abort(404)
	sub = option.post.sub

	if sub in ('furry','vampire','racist','femboy') and not v.house.lower().startswith(sub):
		abort(403, f"You need to be a member of House {sub.capitalize()} to vote on polls in /h/{sub}")

	if option.exclusive == 2:
		if option.post.total_bet_voted(v):
			abort(403, "You can't bet on a closed poll!")
		if not v.charge_account('coins', POLL_BET_COINS): 
			abort(400, f"You don't have {POLL_BET_COINS} coins!")
		g.db.add(v)
		autojanny = get_account(AUTOJANNY_ID)
		autojanny.pay_account('coins', POLL_BET_COINS)
		g.db.add(autojanny)

	if option.exclusive:
		vote = g.db.query(SubmissionOptionVote).join(SubmissionOption).filter(
			SubmissionOptionVote.user_id==v.id,
			SubmissionOptionVote.submission_id==option.submission_id,
			SubmissionOption.exclusive==option.exclusive).one_or_none()
		if vote:
			if option.exclusive == 2: abort(400, "You already voted on this bet!")
			g.db.delete(vote)

	existing = g.db.query(SubmissionOptionVote).filter_by(option_id=option_id, user_id=v.id).one_or_none()
	if not existing:
		vote = SubmissionOptionVote(
			option_id=option_id,
			user_id=v.id,
			submission_id=option.submission_id,
		)
		g.db.add(vote)
	elif existing and not option.exclusive:
		g.db.delete(existing)

	return {"message": "Bet successful!"}

@app.get("/votes/post/option/<option_id>")
@auth_required
def option_votes(option_id, v):
	try:
		option_id = int(option_id)
	except:
		abort(404)
	option = g.db.get(SubmissionOption, option_id)
	if not option: abort(404)
	if option.post.ghost: abort(403)
	ups = g.db.query(SubmissionOptionVote).filter_by(option_id=option_id).order_by(SubmissionOptionVote.created_utc).all()

	return render_template("poll_votes.html",
						v=v,
						thing=option,
						ups=ups)



@app.post("/vote/comment/option/<option_id>")
@is_not_permabanned
def vote_option_comment(option_id, v):
	try:
		option_id = int(option_id)
	except:
		abort(404)
	option = g.db.get(CommentOption, option_id)
	if not option: abort(404)
	sub = option.comment.post.sub
	if sub in ('furry','vampire','racist','femboy') and not v.house.lower().startswith(sub):
		abort(403, f"You need to be a member of House {sub.capitalize()} to vote on polls in /h/{sub}")

	if option.exclusive:
		vote = g.db.query(CommentOptionVote).join(CommentOption).filter(
			CommentOptionVote.user_id==v.id,
			CommentOptionVote.comment_id==option.comment_id,
			CommentOption.exclusive==1).one_or_none()
		if vote:
			g.db.delete(vote)

	existing = g.db.query(CommentOptionVote).filter_by(option_id=option_id, user_id=v.id).one_or_none()
	if not existing:
		vote = CommentOptionVote(
			option_id=option_id,
			user_id=v.id,
			comment_id=option.comment_id,
		)
		g.db.add(vote)
	elif existing:
		g.db.delete(existing)

	return "", 204

@app.get("/votes/comment/option/<option_id>")
@auth_required
def option_votes_comment(option_id, v):
	try:
		option_id = int(option_id)
	except:
		abort(404)
	option = g.db.get(CommentOption, option_id)

	if not option: abort(404)

	if option.comment.ghost: abort(403)

	ups = g.db.query(CommentOptionVote).filter_by(option_id=option_id).order_by(CommentOptionVote.created_utc).all()

	return render_template("poll_votes.html",
						v=v,
						thing=option,
						ups=ups)
