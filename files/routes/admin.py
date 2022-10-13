import time
import re
from os import remove
from PIL import Image as IMAGE

from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.sanitize import *
from files.helpers.security import *
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.const import *
from files.helpers.actions import *
from files.helpers.cloudflare import *
from files.classes import *
from flask import *
from files.__main__ import app, cache, limiter
from .front import frontlist
from .login import check_for_alts
from files.helpers.discord import add_role
import datetime
import requests
from urllib.parse import quote, urlencode

@app.post('/kippy')
@admin_level_required(PERMS['PRINT_MARSEYBUX_FOR_KIPPY_ON_PCMEMES'])
def kippy(v):
	if SITE == 'rdrama.net': abort(404)
	kippy = get_account(KIPPY_ID)
	kippy.procoins += 10000
	g.db.add(kippy)
	return '10k marseycoins printed!'

@app.get('/admin/loggedin')
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedin_list(v):
	ids = [x for x,val in cache.get(f'{SITE}_loggedin').items() if time.time()-val < LOGGEDIN_ACTIVE_TIME]
	users = g.db.query(User).filter(User.id.in_(ids)).order_by(User.admin_level.desc(), User.truecoins.desc()).all()
	return render_template("loggedin.html", v=v, users=users)

@app.get('/admin/loggedout')
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedout_list(v):
	users = sorted([val[1] for x,val in cache.get(f'{SITE}_loggedout').items() if time.time()-val[0] < LOGGEDIN_ACTIVE_TIME])
	return render_template("loggedout.html", v=v, users=users)

@app.get('/admin/merge/<id1>/<id2>')
@admin_level_required(PERMS['USER_MERGE'])
def merge(v, id1, id2):
	if v.id != AEVANN_ID: abort(403)

	if time.time() - session.get('verified', 0) > 3:
		session.pop("lo_user", None)
		path = request.path
		qs = urlencode(dict(request.values))
		argval = quote(f"{path}?{qs}", safe='')
		return redirect(f"/login?redirect={argval}")

	user1 = get_account(id1)
	user2 = get_account(id2)

	awards = g.db.query(AwardRelationship).filter_by(user_id=user2.id)
	comments = g.db.query(Comment).filter_by(author_id=user2.id)
	submissions = g.db.query(Submission).filter_by(author_id=user2.id)
	badges = g.db.query(Badge).filter_by(user_id=user2.id)
	mods = g.db.query(Mod).filter_by(user_id=user2.id)
	exiles = g.db.query(Exile).filter_by(user_id=user2.id)

	for award in awards:
		award.user_id = user1.id
		g.db.add(award)
	for comment in comments:
		comment.author_id = user1.id
		g.db.add(comment)
	for submission in submissions:
		submission.author_id = user1.id
		g.db.add(submission)
	for badge in badges:
		if not user1.has_badge(badge.badge_id):
			badge.user_id = user1.id
			g.db.add(badge)
			g.db.flush()
	for mod in mods:
		if not user1.mods(mod.sub):
			mod.user_id = user1.id
			g.db.add(mod)
			g.db.flush()
	for exile in exiles:
		if not user1.exiled_from(exile.sub):
			exile.user_id = user1.id
			g.db.add(exile)
			g.db.flush()

	for kind in ('comment_count', 'post_count', 'winnings', 'received_award_count', 'coins_spent', 'lootboxes_bought', 'coins', 'truecoins', 'procoins'):
		amount = getattr(user1, kind) + getattr(user2, kind)
		setattr(user1, kind, amount)
		setattr(user2, kind, 0)

	g.db.add(user1)
	g.db.add(user2)

	online = cache.get(ONLINE_STR)
	cache.clear()
	cache.set(ONLINE_STR, online)

	return redirect(user1.url)


@app.get('/admin/merge_all/<id>')
@admin_level_required(PERMS['USER_MERGE'])
def merge_all(v, id):
	if v.id != AEVANN_ID: abort(403)

	if time.time() - session.get('verified', 0) > 3:
		session.pop("lo_user", None)
		path = request.path
		qs = urlencode(dict(request.values))
		argval = quote(f"{path}?{qs}", safe='')
		return redirect(f"/login?redirect={argval}")

	user = get_account(id)

	alt_ids = [x.id for x in user.alts_unique]

	things = g.db.query(AwardRelationship).filter(AwardRelationship.user_id.in_(alt_ids)).all() + g.db.query(Mod).filter(Mod.user_id.in_(alt_ids)).all() + g.db.query(Exile).filter(Exile.user_id.in_(alt_ids)).all()
	for thing in things:
		thing.user_id = user.id
		g.db.add(thing)

	things = g.db.query(Submission).filter(Submission.author_id.in_(alt_ids)).all() + g.db.query(Comment).filter(Comment.author_id.in_(alt_ids)).all()
	for thing in things:
		thing.author_id = user.id
		g.db.add(thing)


	badges = g.db.query(Badge).filter(Badge.user_id.in_(alt_ids)).all()
	for badge in badges:
		if not user.has_badge(badge.badge_id):
			badge.user_id = user.id
			g.db.add(badge)
			g.db.flush()

	for alt in user.alts_unique:
		for kind in ('comment_count', 'post_count', 'winnings', 'received_award_count', 'coins_spent', 'lootboxes_bought', 'coins', 'truecoins', 'procoins'):
			amount = getattr(user, kind) + getattr(alt, kind)
			setattr(user, kind, amount)
			setattr(alt, kind, 0)
		g.db.add(alt)

	g.db.add(user)

	online = cache.get(ONLINE_STR)
	cache.clear()
	cache.set(ONLINE_STR, online)

	return redirect(user.url)


@app.post("/@<username>/make_admin")
@admin_level_required(PERMS['ADMIN_ADD'])
def make_admin(v, username):
	if SITE == 'rdrama.net': abort(403)

	user = get_user(username)

	user.admin_level = PERMS['ADMIN_ADD_PERM_LEVEL']
	g.db.add(user)

	ma = ModAction(
		kind="make_admin",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been made admin!"}


@app.post("/@<username>/remove_admin")
@admin_level_required(PERMS['ADMIN_REMOVE'])
def remove_admin(v, username):
	user = get_user(username)
	user.admin_level = 0
	g.db.add(user)

	ma = ModAction(
		kind="remove_admin",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been removed as admin!"}

@app.post("/distribute/<option_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_BETS_DISTRIBUTE'])
def distribute(v, option_id):
	autojanny = get_account(AUTOJANNY_ID)
	if autojanny.coins == 0: abort(400, "@AutoJanny has 0 coins")

	try: option_id = int(option_id)
	except: abort(400)

	try: option = g.db.get(SubmissionOption, option_id)
	except: abort(404)

	if option.exclusive != 2: abort(403)

	option.exclusive = 3
	g.db.add(option)

	post = option.post

	pool = 0
	for o in post.options:
		if o.exclusive >= 2: pool += o.upvotes
	pool *= POLL_BET_COINS

	autojanny.charge_account('coins', pool)
	if autojanny.coins < 0: autojanny.coins = 0
	g.db.add(autojanny)

	votes = option.votes
	coinsperperson = int(pool / len(votes))

	cid = notif_comment(f"You won {coinsperperson} coins betting on [{post.title}]({post.shortlink}) :marseyparty:")
	for vote in votes:
		u = vote.user
		u.coins += coinsperperson
		add_notif(cid, u.id)


	cid = notif_comment(f"You lost the {POLL_BET_COINS} coins you bet on [{post.title}]({post.shortlink}) :marseylaugh:")
	losing_voters = []
	for o in post.options:
		if o.exclusive == 2:
			losing_voters.extend([x.user_id for x in o.votes])
	for uid in losing_voters:
		add_notif(cid, uid)
	
	ma = ModAction(
		kind="distribute",
		user_id=v.id,
		target_submission_id=post.id
	)
	g.db.add(ma)

	return {"message": f"Each winner has received {coinsperperson} coins!"}

@app.post("/@<username>/revert_actions")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['ADMIN_ACTIONS_REVERT'])
def revert_actions(v, username):
	user = get_user(username)

	ma = ModAction(
		kind="revert",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	cutoff = int(time.time()) - 86400

	posts = [x[0] for x in g.db.query(ModAction.target_submission_id).filter(ModAction.user_id == user.id, ModAction.created_utc > cutoff, ModAction.kind == 'ban_post').all()]
	posts = g.db.query(Submission).filter(Submission.id.in_(posts)).all()

	comments = [x[0] for x in g.db.query(ModAction.target_comment_id).filter(ModAction.user_id == user.id, ModAction.created_utc > cutoff, ModAction.kind == 'ban_comment').all()]
	comments = g.db.query(Comment).filter(Comment.id.in_(comments)).all()

	for item in posts + comments:
		item.is_banned = False
		item.ban_reason = None
		item.is_approved = v.id
		g.db.add(item)

	users = (x[0] for x in g.db.query(ModAction.target_user_id).filter(ModAction.user_id == user.id, ModAction.created_utc > cutoff, ModAction.kind.in_(('shadowban', 'ban_user'))).all())
	users = g.db.query(User).filter(User.id.in_(users)).all()

	for user in users:
		user.shadowbanned = None
		user.unban_utc = 0
		user.ban_reason = None
		if user.is_banned:
			user.is_banned = 0
			send_repeatable_notification(user.id, f"@{v.username} (Admin) has unbanned you!")
		g.db.add(user)

		for u in user.alts:
			u.shadowbanned = None
			u.unban_utc = 0
			u.ban_reason = None
			if u.is_banned:
				u.is_banned = 0
				send_repeatable_notification(u.id, f"@{v.username} (Admin) has unbanned you!")
			g.db.add(u)

	return {"message": f"@{user.username}'s admin actions have been reverted!"}

@app.post("/@<username>/club_allow")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_CLUB_ALLOW_BAN'])
def club_allow(v, username):
	u = get_user(username, v=v)

	if u.admin_level >= v.admin_level: abort(403, 'noob')

	u.club_allowed = True
	g.db.add(u)

	for x in u.alts_unique:
		x.club_allowed = True
		g.db.add(x)

	ma = ModAction(
		kind="club_allow",
		user_id=v.id,
		target_user_id=u.id
	)
	g.db.add(ma)

	send_repeatable_notification(u.id, f"@{v.username} (Admin) has inducted you into the {CC_TITLE}!")

	return {"message": f"@{u.username} has been allowed into the {CC_TITLE}!"}

@app.post("/@<username>/club_ban")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_CLUB_ALLOW_BAN'])
def club_ban(v, username):
	u = get_user(username, v=v)

	if u.admin_level >= v.admin_level: abort(403, 'noob')

	u.club_allowed = False

	for x in u.alts_unique:
		u.club_allowed = False
		g.db.add(x)

	ma = ModAction(
		kind="club_ban",
		user_id=v.id,
		target_user_id=u.id
	)
	g.db.add(ma)

	send_repeatable_notification(u.id, f"@{v.username} (Admin) has disallowed you from the {CC_TITLE}!")

	return {"message": f"@{u.username} has been disallowed from the {CC_TITLE}. Deserved."}


@app.get("/admin/shadowbanned")
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowbanned(v):
	users = g.db.query(User).filter(User.shadowbanned != None).order_by(User.shadowbanned).all()
	return render_template("shadowbanned.html", v=v, users=users)


@app.get("/admin/image_posts")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def image_posts_listing(v):

	try: page = int(request.values.get('page', 1))
	except: page = 1

	posts = g.db.query(Submission).order_by(Submission.id.desc())

	firstrange = 25 * (page - 1)
	secondrange = firstrange+26
	posts = [x.id for x in posts if x.is_image][firstrange:secondrange]
	next_exists = (len(posts) > 25)
	posts = get_posts(posts[:25], v=v)

	return render_template("admin/image_posts.html", v=v, listing=posts, next_exists=next_exists, page=page, sort="new")


@app.get("/admin/reported/posts")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_posts(v):

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Submission).filter_by(
		is_approved=None,
		is_banned=False
	).join(Submission.flags).order_by(Submission.id.desc()).offset(25 * (page - 1)).limit(26)

	listing = [p.id for p in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_posts(listing, v=v)

	return render_template("admin/reported_posts.html",
						next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/admin/reported/comments")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_comments(v):

	page = max(1, int(request.values.get("page", 1)))

	listing = g.db.query(Comment
					).filter_by(
		is_approved=None,
		is_banned=False
	).join(Comment.flags).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > 25
	listing = listing[:25]

	listing = get_comments(listing, v=v)

	return render_template("admin/reported_comments.html",
						next_exists=next_exists,
						listing=listing,
						page=page,
						v=v,
						standalone=True)

@app.get("/admin")
@admin_level_required(PERMS['ADMIN_HOME_VISIBLE'])
def admin_home(v):
	under_attack = False

	if v.admin_level >= PERMS['SITE_SETTINGS_UNDER_ATTACK']:
		under_attack = (get_security_level() or 'high') == 'under_attack'

	gitref = admin_git_head()
	
	return render_template("admin/admin_home.html", v=v, 
		under_attack=under_attack, 
		gitref=gitref)

def admin_git_head():
	short_len = 12
	# Note: doing zero sanitization. Git branch names are extremely permissive.
	# However, they forbid '..', so I don't see an obvious dir traversal attack.
	# Also, a malicious branch name would mean someone already owned the server
	# or repo, so I think this isn't a weak link.
	try:
		with open('.git/HEAD', encoding='utf_8') as head_f:
			head_txt = head_f.read()
			head_path = git_regex.match(head_txt).group(1)
			with open('.git/' + head_path, encoding='utf_8') as ref_f:
				gitref = ref_f.read()[0:short_len]
	except:
		return '<unable to read>'
	return gitref

@app.post("/admin/site_settings/<setting>")
@admin_level_required(PERMS['SITE_SETTINGS'])
def change_settings(v, setting):
	site_settings = app.config['SETTINGS']
	site_settings[setting] = not site_settings[setting] 
	with open("/site_settings.json", "w", encoding='utf_8') as f:
		json.dump(site_settings, f)

	if site_settings[setting]: word = 'enable'
	else: word = 'disable'

	ma = ModAction(
		kind=f"{word}_{setting}",
		user_id=v.id,
	)
	g.db.add(ma)


	return {'message': f"{setting} {word}d successfully!"}


@app.post("/admin/purge_cache")
@admin_level_required(PERMS['SITE_CACHE_PURGE_CDN'])
def purge_cache(v):
	online = cache.get(ONLINE_STR)
	cache.clear()
	cache.set(ONLINE_STR, online)
	if not purge_entire_cache():
		abort(400, 'Failed to purge cache')
	ma = ModAction(
		kind="purge_cache",
		user_id=v.id
	)
	g.db.add(ma)
	return {"message": "Cache purged!"}


@app.post("/admin/under_attack")
@admin_level_required(PERMS['SITE_SETTINGS_UNDER_ATTACK'])
def under_attack(v):
	response = get_security_level()
	if not response:
		abort(400, 'Could not retrieve the current security level')
	old_under_attack_mode = response == 'under_attack'
	enable_disable_str = 'disable' if old_under_attack_mode else 'enable'
	new_security_level = 'high' if old_under_attack_mode else 'under_attack'
	if not set_security_level(new_security_level):
		abort(400, f'Failed to {enable_disable_str} under attack mode')
	ma = ModAction(
		kind=f"{enable_disable_str}_under_attack",
		user_id=v.id,
	)
	g.db.add(ma)
	return {"message": f"Under attack mode {enable_disable_str}d!"}

@app.get("/admin/badge_grant")
@admin_level_required(PERMS['USER_BADGES'])
@feature_required('BADGES')
def badge_grant_get(v):
	badges = g.db.query(BadgeDef).order_by(BadgeDef.id).all()
	return render_template("admin/badge_grant.html", v=v, badge_types=badges)


@app.post("/admin/badge_grant")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_BADGES'])
@feature_required('BADGES')
def badge_grant_post(v):
	

	badges = g.db.query(BadgeDef).order_by(BadgeDef.id).all()

	user = get_user(request.values.get("username").strip(), graceful=True)
	if not user:
		return render_template("admin/badge_grant.html", v=v, badge_types=badges, error="User not found.")

	try: badge_id = int(request.values.get("badge_id"))
	except: abort(400)

	if badge_id in {16,17,21,22,23,24,25,26,27,94,95,96,97,98,109,137} and v.id != AEVANN_ID and SITE != 'pcmemes.net':
		abort(403)

	if user.has_badge(badge_id):
		return render_template("admin/badge_grant.html", v=v, badge_types=badges, error="User already has that badge.")
	
	new_badge = Badge(badge_id=badge_id, user_id=user.id)

	desc = request.values.get("description")
	if desc: new_badge.description = desc

	url = request.values.get("url")
	if '\\' in url: abort(400)

	if url: new_badge.url = url

	g.db.add(new_badge)
	g.db.flush()

	if v.id != user.id:
		text = f"@{v.username} (Admin) has given you the following profile badge:\n\n![]({new_badge.path})\n\n**{new_badge.name}**\n\n{new_badge.badge.description}"
		send_repeatable_notification(user.id, text)
	
	ma = ModAction(
		kind="badge_grant",
		user_id=v.id,
		target_user_id=user.id,
		_note=new_badge.name
	)
	g.db.add(ma)

	return render_template("admin/badge_grant.html", v=v, badge_types=badges, msg=f"{new_badge.name} Badge granted to @{user.username} successfully!")



@app.get("/admin/badge_remove")
@admin_level_required(PERMS['USER_BADGES'])
@feature_required('BADGES')
def badge_remove_get(v):
	

	badges = g.db.query(BadgeDef).order_by(BadgeDef.id).all()

	return render_template("admin/badge_remove.html", v=v, badge_types=badges)


@app.post("/admin/badge_remove")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_BADGES'])
@feature_required('BADGES')
def badge_remove_post(v):
	
	
	badges = g.db.query(BadgeDef).order_by(BadgeDef.id).all()

	user = get_user(request.values.get("username").strip(), graceful=True)
	if not user:
		return render_template("admin/badge_remove.html", v=v, badge_types=badges, error="User not found.")

	try: badge_id = int(request.values.get("badge_id"))
	except: abort(400)

	badge = user.has_badge(badge_id)
	if not badge:
		return render_template("admin/badge_remove.html", v=v, badge_types=badges, error="User doesn't have that badge.")

	if v.id != user.id:
		text = f"@{v.username} (Admin) has removed the following profile badge from you:\n\n![]({badge.path})\n\n**{badge.name}**\n\n{badge.badge.description}"
		send_repeatable_notification(user.id, text)

	ma = ModAction(
		kind="badge_remove",
		user_id=v.id,
		target_user_id=user.id,
		_note=badge.name
	)
	g.db.add(ma)

	g.db.delete(badge)


	return render_template("admin/badge_remove.html", v=v, badge_types=badges, msg=f"{badge.name} Badge removed from @{user.username} successfully!")


@app.get("/admin/users")
@admin_level_required(PERMS['VIEW_ALL_USERS'])
def users_list(v):

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(User).order_by(User.id.desc()).offset(25 * (page - 1)).limit(26).all()

	next_exists = (len(users) > 25)
	users = users[:25]

	return render_template("user_cards.html",
						v=v,
						users=users,
						next_exists=next_exists,
						page=page,
						)



@app.get("/admin/alt_votes")
@admin_level_required(PERMS['VIEW_ALT_VOTES'])
def alt_votes_get(v):

	u1 = request.values.get("u1")
	u2 = request.values.get("u2")

	if not u1 or not u2:
		return render_template("admin/alt_votes.html", v=v)

	u1 = get_user(u1)
	u2 = get_user(u2)

	u1_post_ups = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_post_downs = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u1_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u2_post_ups = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_post_downs = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()
	u2_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()

	data = {}
	data['u1_only_post_ups'] = len(
		[x for x in u1_post_ups if x not in u2_post_ups])
	data['u2_only_post_ups'] = len(
		[x for x in u2_post_ups if x not in u1_post_ups])
	data['both_post_ups'] = len(list(set(u1_post_ups) & set(u2_post_ups)))

	data['u1_only_post_downs'] = len(
		[x for x in u1_post_downs if x not in u2_post_downs])
	data['u2_only_post_downs'] = len(
		[x for x in u2_post_downs if x not in u1_post_downs])
	data['both_post_downs'] = len(
		list(set(u1_post_downs) & set(u2_post_downs)))

	data['u1_only_comment_ups'] = len(
		[x for x in u1_comment_ups if x not in u2_comment_ups])
	data['u2_only_comment_ups'] = len(
		[x for x in u2_comment_ups if x not in u1_comment_ups])
	data['both_comment_ups'] = len(
		list(set(u1_comment_ups) & set(u2_comment_ups)))

	data['u1_only_comment_downs'] = len(
		[x for x in u1_comment_downs if x not in u2_comment_downs])
	data['u2_only_comment_downs'] = len(
		[x for x in u2_comment_downs if x not in u1_comment_downs])
	data['both_comment_downs'] = len(
		list(set(u1_comment_downs) & set(u2_comment_downs)))

	data['u1_post_ups_unique'] = 100 * \
		data['u1_only_post_ups'] // len(u1_post_ups) if u1_post_ups else 0
	data['u2_post_ups_unique'] = 100 * \
		data['u2_only_post_ups'] // len(u2_post_ups) if u2_post_ups else 0
	data['u1_post_downs_unique'] = 100 * \
		data['u1_only_post_downs'] // len(
			u1_post_downs) if u1_post_downs else 0
	data['u2_post_downs_unique'] = 100 * \
		data['u2_only_post_downs'] // len(
			u2_post_downs) if u2_post_downs else 0

	data['u1_comment_ups_unique'] = 100 * \
		data['u1_only_comment_ups'] // len(
			u1_comment_ups) if u1_comment_ups else 0
	data['u2_comment_ups_unique'] = 100 * \
		data['u2_only_comment_ups'] // len(
			u2_comment_ups) if u2_comment_ups else 0
	data['u1_comment_downs_unique'] = 100 * \
		data['u1_only_comment_downs'] // len(
			u1_comment_downs) if u1_comment_downs else 0
	data['u2_comment_downs_unique'] = 100 * \
		data['u2_only_comment_downs'] // len(
			u2_comment_downs) if u2_comment_downs else 0

	return render_template("admin/alt_votes.html",
						u1=u1,
						u2=u2,
						v=v,
						data=data
						)


@app.post("/admin/link_accounts")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_LINK'])
def admin_link_accounts(v):

	u1 = int(request.values.get("u1"))
	u2 = int(request.values.get("u2"))

	new_alt = Alt(
		user1=u1, 
		user2=u2,
		is_manual=True
		)

	g.db.add(new_alt)
	g.db.flush()

	check_for_alts(g.db.get(User, u1))
	check_for_alts(g.db.get(User, u2))

	ma = ModAction(
		kind="link_accounts",
		user_id=v.id,
		target_user_id=u1,
		_note=f'with {u2}'
	)
	g.db.add(ma)

	return redirect(f"/admin/alt_votes?u1={get_account(u1).username}&u2={get_account(u2).username}")


@app.get("/admin/removed/posts")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed(v):

	try: page = int(request.values.get("page", 1))
	except: page = 1

	if page < 1: abort(400)
	
	ids = g.db.query(Submission.id).join(Submission.author).filter(or_(Submission.is_banned==True, User.shadowbanned != None)).order_by(Submission.id.desc()).offset(25 * (page - 1)).limit(26).all()

	ids=[x[0] for x in ids]

	next_exists = len(ids) > 25

	ids = ids[:25]

	posts = get_posts(ids, v=v)

	return render_template("admin/removed_posts.html",
						v=v,
						listing=posts,
						page=page,
						next_exists=next_exists
						)


@app.get("/admin/removed/comments")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed_comments(v):

	try: page = int(request.values.get("page", 1))
	except: page = 1
	
	ids = g.db.query(Comment.id).join(Comment.author).filter(or_(Comment.is_banned==True, User.shadowbanned != None)).order_by(Comment.id.desc()).offset(25 * (page - 1)).limit(26).all()

	ids=[x[0] for x in ids]

	next_exists = len(ids) > 25

	ids = ids[:25]

	comments = get_comments(ids, v=v)

	return render_template("admin/removed_comments.html",
						v=v,
						listing=comments,
						page=page,
						next_exists=next_exists
						)


@app.post("/agendaposter/<user_id>")
@admin_level_required(PERMS['USER_AGENDAPOSTER'])
def agendaposter(user_id, v):
	user = get_account(user_id)

	days = request.values.get("days")

	if days:
		expiry = int(time.time() + float(days)*60*60*24)
	else: expiry = 1

	user.agendaposter = expiry
	g.db.add(user)

	if days:
		days_txt = str(days).rstrip('.0')
		note = f"for {days_txt} days"
	else: note = "permanently"

	ma = ModAction(
		kind="agendaposter",
		user_id=v.id,
		target_user_id=user.id,
		_note=note
	)
	g.db.add(ma)

	badge_grant(user=user, badge_id=28)

	send_repeatable_notification(user.id, f"@{v.username} (Admin) has marked you as a chud ({note}).")

	
	return redirect(user.url)



@app.post("/unagendaposter/<user_id>")
@admin_level_required(PERMS['USER_AGENDAPOSTER'])
def unagendaposter(user_id, v):
	user = get_account(user_id)

	user.agendaposter = 0
	g.db.add(user)

	for alt in user.alts:
		alt.agendaposter = 0
		g.db.add(alt)

	ma = ModAction(
		kind="unagendaposter",
		user_id=v.id,
		target_user_id=user.id
	)

	g.db.add(ma)

	badge = user.has_badge(28)
	if badge: g.db.delete(badge)

	send_repeatable_notification(user.id, f"@{v.username} (Admin) has unmarked you as a chud.")

	return {"message": f"@{user.username}'s chud theme has been disabled!"}


@app.post("/shadowban/<user_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowban(user_id, v):
	user = get_account(user_id)
	if user.admin_level != 0: abort(403)
	user.shadowbanned = v.username
	reason = request.values.get("reason").strip()[:256]
	user.ban_reason = reason
	g.db.add(user)

	if request.values.get("alts"):
		for alt in user.alts:
			if alt.admin_level: continue
			alt.shadowbanned = v.username
			alt.ban_reason = reason
			g.db.add(alt)

	ma = ModAction(
		kind="shadowban",
		user_id=v.id,
		target_user_id=user.id,
		_note=f'reason: "{reason}"'
	)
	g.db.add(ma)
	
	cache.delete_memoized(frontlist)

	return redirect(user.url)

@app.post("/unshadowban/<user_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_SHADOWBAN'])
def unshadowban(user_id, v):
	user = get_account(user_id)
	user.shadowbanned = None
	if not user.is_banned: user.ban_reason = None
	g.db.add(user)
	for alt in user.alts:
		alt.shadowbanned = None
		if not alt.is_banned: alt.ban_reason = None
		g.db.add(alt)

	ma = ModAction(
		kind="unshadowban",
		user_id=v.id,
		target_user_id=user.id,
	)
	g.db.add(ma)
	
	cache.delete_memoized(frontlist)

	return redirect(user.url)


@app.post("/admin/title_change/<user_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_TITLE_CHANGE'])
def admin_title_change(user_id, v):

	user = get_account(user_id)

	new_name=request.values.get("title").strip()[:256]

	user.customtitleplain=new_name
	new_name = filter_emojis_only(new_name)

	user=get_account(user.id)
	user.customtitle=new_name
	if request.values.get("locked"): user.flairchanged = int(time.time()) + 2629746
	else:
		user.flairchanged = None
		badge = user.has_badge(96)
		if badge: g.db.delete(badge)

	g.db.add(user)

	if user.flairchanged: kind = "set_flair_locked"
	else: kind = "set_flair_notlocked"
	
	ma=ModAction(
		kind=kind,
		user_id=v.id,
		target_user_id=user.id,
		_note=f'"{user.customtitleplain}"'
		)
	g.db.add(ma)

	return redirect(user.url)

@app.post("/ban_user/<user_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_BAN'])
def ban_user(user_id, v):
	user = get_account(user_id)

	if user.admin_level > v.admin_level:
		abort(403)

	days = float(request.values.get("days")) if request.values.get('days') else 0

	reason = request.values.get("reason").strip()[:256]
	reason = filter_emojis_only(reason)

	if reason.startswith("/") and '\\' not in reason: 
		reason = f'<a href="{reason.split()[0]}">{reason}</a>'

	user.ban(admin=v, reason=reason, days=days)

	if request.values.get("alts"):
		for x in user.alts:
			if x.admin_level > v.admin_level:
				continue
			x.ban(admin=v, reason=reason, days=days)

	if days:
		days_txt = str(days).rstrip('.0')
		if reason: text = f"@{v.username} (Admin) has banned you for **{days_txt}** days for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (Admin) has banned you for **{days_txt}** days."
	else:
		if reason: text = f"@{v.username} (Admin) has banned you permanently for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (Admin) has banned you permanently."

	send_repeatable_notification(user.id, text)
	
	if days == 0: duration = "permanently"
	elif days == 1: duration = "for 1 day"
	else: duration = f"for {days_txt} days"

	note = f'reason: "{reason}", duration: {duration}'
	ma=ModAction(
		kind="ban_user",
		user_id=v.id,
		target_user_id=user.id,
		_note=note
		)
	g.db.add(ma)

	if 'reason' in request.values:
		if request.values["reason"].startswith("/post/"):
			try: post = int(request.values["reason"].split("/post/")[1].split(None, 1)[0])
			except: abort(400)
			post = get_post(post)
			post.bannedfor = f'{duration} by @{v.username}'
			g.db.add(post)
		elif request.values["reason"].startswith("/comment/"):
			try: comment = int(request.values["reason"].split("/comment/")[1].split(None, 1)[0])
			except: abort(400)
			comment = get_comment(comment)
			comment.bannedfor = f'{duration} by @{v.username}'
			g.db.add(comment)

	if 'redir' in request.values: return redirect(user.url)
	else: return {"message": f"@{user.username} has been banned!"}


@app.post("/unban_user/<user_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_BAN'])
def unban_user(user_id, v):
	user = get_account(user_id)
	if not user.is_banned:
		abort(400)

	user.is_banned = 0
	user.unban_utc = 0
	user.ban_reason = None
	send_repeatable_notification(user.id, f"@{v.username} (Admin) has unbanned you!")
	g.db.add(user)

	for x in user.alts:
		if x.is_banned: send_repeatable_notification(x.id, f"@{v.username} (Admin) has unbanned you!")
		x.is_banned = 0
		x.unban_utc = 0
		x.ban_reason = None
		g.db.add(x)

	ma=ModAction(
		kind="unban_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	if "@" in request.referrer: return redirect(user.url)
	else: return {"message": f"@{user.username} has been unbanned!"}

@app.post("/mute_user/<int:user_id>/<int:mute_status>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['USER_BAN'])
def mute_user(v, user_id, mute_status):
	user = get_account(user_id)

	if mute_status != 0 and not user.is_muted:
		user.is_muted = True
		log_action = 'mod_mute_user'
		success_msg = f"@{user.username} has been muted!"
	elif mute_status == 0 and user.is_muted:
		user.is_muted = False
		log_action = 'mod_unmute_user'
		success_msg = f"@{user.username} has been un-muted!"
	else:
		abort(400)

	ma = ModAction(
			kind=log_action,
			user_id=v.id,
			target_user_id=user.id,
			)

	g.db.add(user)
	g.db.add(ma)
	if 'redir' in request.values:
		return redirect(user.url)
	else:
		return {"message": success_msg}

@app.post("/remove_post/<post_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_post(post_id, v):
	post = get_post(post_id)
	post.is_banned = True
	post.is_approved = None
	post.stickied = None
	post.is_pinned = False
	post.ban_reason = v.username
	g.db.add(post)

	

	ma=ModAction(
		kind="ban_post",
		user_id=v.id,
		target_submission_id=post.id,
		)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	v.coins += 1
	g.db.add(v)
	purge_files_in_cache(f"https://{SITE}/logged_out")
	return {"message": "Post removed!"}


@app.post("/approve_post/<post_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_post(post_id, v):

	post = get_post(post_id)

	if post.author.id == v.id and post.author.agendaposter and AGENDAPOSTER_PHRASE not in post.body.lower() and post.sub != 'chudrama':
		abort(400, "You can't bypass the chud award!")

	if post.is_banned:
		ma=ModAction(
			kind="unban_post",
			user_id=v.id,
			target_submission_id=post.id,
		)
		g.db.add(ma)

	post.is_banned = False
	post.ban_reason = None
	post.is_approved = v.id

	g.db.add(post)

	cache.delete_memoized(frontlist)

	v.charge_account('coins', 1)
	g.db.add(v)

	return {"message": "Post approved!"}


@app.post("/distinguish/<post_id>")
@admin_level_required(PERMS['POST_COMMENT_DISTINGUISH'])
def distinguish_post(post_id, v):
	post = get_post(post_id)

	if post.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']: abort(403)

	if post.distinguish_level:
		post.distinguish_level = 0
		kind = 'undistinguish_post'
	else:
		post.distinguish_level = v.admin_level
		kind = 'distinguish_post'

	g.db.add(post)

	ma = ModAction(
		kind=kind,
		user_id=v.id,
		target_submission_id=post.id
	)
	g.db.add(ma)


	if post.distinguish_level: return {"message": "Post distinguished!"}
	else: return {"message": "Post undistinguished!"}


@app.post("/sticky/<post_id>")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
@feature_required('PINS')
def sticky_post(post_id, v):
	

	post = get_post(post_id)
	if not post.stickied:
		pins = g.db.query(Submission).filter(Submission.stickied != None, Submission.is_banned == False).count()
		if pins >= PIN_LIMIT:
			if v.admin_level >= PERMS['BYPASS_PIN_LIMIT']:
				post.stickied = v.username
				post.stickied_utc = int(time.time()) + 3600
			else: abort(403, f"Can't exceed {PIN_LIMIT} pinned posts limit!")
		else: post.stickied = v.username
		g.db.add(post)

		ma=ModAction(
			kind="pin_post",
			user_id=v.id,
			target_submission_id=post.id
		)
		g.db.add(ma)

		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (Admin) has pinned [{post.title}](/post/{post_id})!")

		cache.delete_memoized(frontlist)
	return {"message": "Post pinned!"}

@app.post("/unsticky/<post_id>")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def unsticky_post(post_id, v):

	post = get_post(post_id)
	if post.stickied:
		if post.stickied.endswith('(pin award)'): abort(403, "Can't unpin award pins!")

		post.stickied = None
		post.stickied_utc = None
		g.db.add(post)

		ma=ModAction(
			kind="unpin_post",
			user_id=v.id,
			target_submission_id=post.id
		)
		g.db.add(ma)

		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (Admin) has unpinned [{post.title}](/post/{post_id})!")

		cache.delete_memoized(frontlist)
	return {"message": "Post unpinned!"}

@app.post("/sticky_comment/<cid>")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def sticky_comment(cid, v):
	
	comment = get_comment(cid, v=v)

	if not comment.stickied:
		comment.stickied = v.username
		g.db.add(comment)

		ma=ModAction(
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (Admin) has pinned your [comment]({comment.shortlink})!"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}
	

@app.post("/unsticky_comment/<cid>")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def unsticky_comment(cid, v):
	
	comment = get_comment(cid, v=v)
	
	if comment.stickied:
		if comment.stickied.endswith("(pin award)"): abort(403, "Can't unpin award pins!")

		comment.stickied = None
		g.db.add(comment)

		ma=ModAction(
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (Admin) has unpinned your [comment]({comment.shortlink})!"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment unpinned!"}


@app.post("/remove_comment/<c_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_comment(c_id, v):
	comment = get_comment(c_id)

	comment.is_banned = True
	comment.is_approved = None
	comment.ban_reason = v.username
	g.db.add(comment)
	ma=ModAction(
		kind="ban_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	return {"message": "Comment removed!"}


@app.post("/approve_comment/<c_id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_comment(c_id, v):

	comment = get_comment(c_id)
	if not comment: abort(404)
	
	if comment.author.id == v.id and comment.author.agendaposter and AGENDAPOSTER_PHRASE not in comment.body.lower() and comment.post.sub != 'chudrama':
		abort(400, "You can't bypass the chud award!")

	if comment.is_banned:
		ma=ModAction(
			kind="unban_comment",
			user_id=v.id,
			target_comment_id=comment.id,
			)
		g.db.add(ma)

	comment.is_banned = False
	comment.ban_reason = None
	comment.is_approved = v.id

	g.db.add(comment)

	return {"message": "Comment approved!"}


@app.post("/distinguish_comment/<c_id>")
@admin_level_required(PERMS['POST_COMMENT_DISTINGUISH'])
def admin_distinguish_comment(c_id, v):
	
	
	comment = get_comment(c_id, v=v)

	if comment.author_id != v.id: abort(403)

	if comment.distinguish_level:
		comment.distinguish_level = 0
		kind = 'undistinguish_comment'
	else:
		comment.distinguish_level = v.admin_level
		kind = 'distinguish_comment'

	g.db.add(comment)

	ma = ModAction(
		kind=kind,
		user_id=v.id,
		target_comment_id=comment.id
	)
	g.db.add(ma)


	if comment.distinguish_level: return {"message": "Comment distinguished!"}
	else: return {"message": "Comment undistinguished!"}

@app.get("/admin/dump_cache")
@admin_level_required(PERMS['SITE_CACHE_DUMP_INTERNAL'])
def admin_dump_cache(v):
	online = cache.get(ONLINE_STR)
	cache.clear()
	cache.set(ONLINE_STR, online)

	ma = ModAction(
		kind="dump_cache",
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Internal cache cleared."}


@app.get("/admin/banned_domains/")
@admin_level_required(PERMS['DOMAINS_BAN'])
def admin_banned_domains(v):

	banned_domains = g.db.query(BannedDomain).all()
	return render_template("admin/banned_domains.html", v=v, banned_domains=banned_domains)

@app.post("/admin/banned_domains")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['DOMAINS_BAN'])
def admin_toggle_ban_domain(v):

	domain=request.values.get("domain", "").strip()
	if not domain: abort(400)

	reason=request.values.get("reason").strip()

	d = g.db.query(BannedDomain).filter_by(domain=domain).one_or_none()
	if d:
		g.db.delete(d)
		ma = ModAction(
			kind="unban_domain",
			user_id=v.id,
			_note=domain
		)
		g.db.add(ma)

	else:
		d = BannedDomain(domain=domain, reason=reason)
		g.db.add(d)
		ma = ModAction(
			kind="ban_domain",
			user_id=v.id,
			_note=f'{domain}, reason: {reason}'
		)
		g.db.add(ma)


	return redirect("/admin/banned_domains/")

@app.post("/admin/nuke_user")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_nuke_user(v):

	user=get_user(request.values.get("user"))

	for post in g.db.query(Submission).filter_by(author_id=user.id).all():
		if post.is_banned:
			continue
			
		post.is_banned = True
		post.ban_reason = v.username
		g.db.add(post)

	for comment in g.db.query(Comment).filter_by(author_id=user.id).all():
		if comment.is_banned:
			continue

		comment.is_banned = True
		comment.ban_reason = v.username
		g.db.add(comment)

	ma=ModAction(
		kind="nuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return redirect(user.url)


@app.post("/admin/unnuke_user")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_nunuke_user(v):

	user=get_user(request.values.get("user"))

	for post in g.db.query(Submission).filter_by(author_id=user.id).all():
		if not post.is_banned:
			continue
			
		post.is_banned = False
		post.ban_reason = None
		post.is_approved = v.id
		g.db.add(post)

	for comment in g.db.query(Comment).filter_by(author_id=user.id).all():
		if not comment.is_banned:
			continue

		comment.is_banned = False
		comment.ban_reason = None
		comment.is_approved = v.id
		g.db.add(comment)

	ma=ModAction(
		kind="unnuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return redirect(user.url)
