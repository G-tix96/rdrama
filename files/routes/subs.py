from files.__main__ import app, limiter
from files.helpers.alerts import *
from files.helpers.wrappers import *
from files.helpers.get import *
from files.helpers.regex import *
from files.classes import *
from .front import frontlist
from sqlalchemy import nullslast
import tldextract

@app.post("/exile/post/<pid>")
@is_not_permabanned
def exile_post(v, pid):
	if v.shadowbanned: return {"error": "Internal Server Error"}, 500
	p = get_post(pid)
	sub = p.sub
	if not sub: abort(400)

	if not v.mods(sub): abort(403)

	u = p.author

	if u.mods(sub): abort(403)

	if not u.exiled_from(sub):
		exile = Exile(user_id=u.id, sub=sub, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{sub} for [{p.title}]({p.shortlink})")

		ma = SubAction(
			sub=sub,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="{p.permalink}">{p.title_html}</a>'
		)
		g.db.add(ma)
	
	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}



@app.post("/exile/comment/<cid>")
@is_not_permabanned
def exile_comment(v, cid):
	if v.shadowbanned: return {"error": "Internal Server Error"}, 500
	c = get_comment(cid)
	sub = c.post.sub
	if not sub: abort(400)

	if not v.mods(sub): abort(403)

	u = c.author

	if u.mods(sub): abort(403)

	if not u.exiled_from(sub):
		exile = Exile(user_id=u.id, sub=sub, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{sub} for [{c.permalink}]({c.shortlink})")

		ma = SubAction(
			sub=sub,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="/comment/{c.id}?context=8#context">comment</a>'
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}


@app.post("/h/<sub>/unexile/<uid>")
@is_not_permabanned
def unexile(v, sub, uid):
	u = get_account(uid)

	if not v.mods(sub): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/exilees')

	if u.exiled_from(sub):
		exile = g.db.query(Exile).filter_by(user_id=u.id, sub=sub).one_or_none()
		g.db.delete(exile)

		send_notification(u.id, f"@{v.username} has revoked your exile from /h/{sub}")

		ma = SubAction(
			sub=sub,
			kind='unexile_user',
			user_id=v.id,
			target_user_id=u.id
		)
		g.db.add(ma)
	
	if request.headers.get("Authorization") or request.headers.get("xhr"):
		return {"message": f"@{u.username} has been unexiled from /h/{sub} successfully!"}

	
	return redirect(f'/h/{sub}/exilees')



@app.post("/h/<sub>/block")
@auth_required
def block_sub(v, sub):
	sub = get_sub_by_name(sub).name
	existing = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub).one_or_none()

	if not existing:
		block = SubBlock(user_id=v.id, sub=sub)
		g.db.add(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} blocked successfully!"}


@app.post("/h/<sub>/unblock")
@auth_required
def unblock_sub(v, sub):
	sub = get_sub_by_name(sub).name
	if sub == "chudrama" and not v.can_see_chudrama: abort(403)
	block = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub).one_or_none()

	if block:
		g.db.delete(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unblocked successfully!"}


@app.post("/h/<sub>/subscribe")
@auth_required
def subscribe_sub(v, sub):
	sub = get_sub_by_name(sub).name
	existing = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()

	if not existing:
		subscribe = SubJoin(user_id=v.id, sub=sub)
		g.db.add(subscribe)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unblocked successfully!"}

@app.post("/h/<sub>/unsubscribe")
@auth_required
def unsubscribe_sub(v, sub):
	sub = get_sub_by_name(sub).name
	subscribe = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()

	if subscribe:
		g.db.delete(subscribe)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} blocked successfully!"}

@app.post("/h/<sub>/follow")
@auth_required
def follow_sub(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	existing = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	if not existing:
		subscription = SubSubscription(user_id=v.id, sub=sub.name)
		g.db.add(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} followed successfully!"}

@app.post("/h/<sub>/unfollow")
@auth_required
def unfollow_sub(v, sub):
	sub = get_sub_by_name(sub)
	subscription = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	if subscription:
		g.db.delete(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unfollowed successfully!"}

@app.get("/h/<sub>/mods")
@auth_required
def mods(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	users = g.db.query(User, Mod).join(Mod).filter_by(sub=sub.name).order_by(Mod.created_utc).all()

	return render_template("sub/mods.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/exilees")
@auth_required
def sub_exilees(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	users = g.db.query(User, Exile).join(Exile, Exile.user_id==User.id) \
				.filter_by(sub=sub.name) \
				.order_by(nullslast(Exile.created_utc.desc()), User.username).all()

	return render_template("sub/exilees.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/blockers")
@auth_required
def sub_blockers(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	users = g.db.query(User).join(SubBlock) \
				.filter_by(sub=sub.name) \
				.order_by(nullslast(SubBlock.created_utc.desc()), User.username).all()

	return render_template("sub/blockers.html", 
		v=v, sub=sub, users=users, verb="blocking")


@app.get("/h/<sub>/followers")
@auth_required
def sub_followers(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	users = g.db.query(User).join(SubSubscription) \
			.filter_by(sub=sub.name) \
			.order_by(nullslast(SubSubscription.created_utc.desc()), User.username).all()

	return render_template("sub/blockers.html", 
		v=v, sub=sub, users=users, verb="following")


@app.post("/h/<sub>/add_mod")
@limiter.limit("1/second;30/day")
@limiter.limit("1/second;30/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def add_mod(v, sub):
	if SITE_NAME == 'WPD': abort(403)
	sub = get_sub_by_name(sub).name
	if not v.mods(sub): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/mods')

	user = request.values.get('user')

	if not user: abort(400)

	user = get_user(user, v=v, include_shadowbanned=False)

	if sub in ('furry','vampire','racist','femboy') and not v.client and not user.house.lower().startswith(sub):
		return {"error": f"@{user.username} needs to be a member of House {sub.capitalize()} to be added as a mod there!"}, 400

	existing = g.db.query(Mod).filter_by(user_id=user.id, sub=sub).one_or_none()

	if not existing:
		mod = Mod(user_id=user.id, sub=sub)
		g.db.add(mod)

		if v.id != user.id:
			send_repeatable_notification(user.id, f"@{v.username} has added you as a mod to /h/{sub}")

		ma = SubAction(
			sub=sub,
			kind='make_mod',
			user_id=v.id,
			target_user_id=user.id
		)
		g.db.add(ma)

	return redirect(f'/h/{sub}/mods')


@app.post("/h/<sub>/remove_mod")
@is_not_permabanned
def remove_mod(v, sub):
	sub = get_sub_by_name(sub).name
	
	if not v.mods(sub): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/mods')

	uid = request.values.get('uid')

	if not uid: abort(400)

	try: uid = int(uid)
	except: abort(400)

	user = get_account(uid)

	if not user: abort(404)

	mod = g.db.query(Mod).filter_by(user_id=user.id, sub=sub).one_or_none()
	if not mod: abort(400)

	if not (v.id == user.id or v.mod_date(sub) and v.mod_date(sub) < mod.created_utc): abort(403)

	g.db.delete(mod)

	if v.id != user.id:
		send_repeatable_notification(user.id, f"@{v.username} has removed you as a mod from /h/{sub}")

	ma = SubAction(
		sub=sub,
		kind='remove_mod',
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/mods')

@app.get("/create_hole")
@is_not_permabanned
def create_sub(v):
	if not v.can_create_hole:
		abort(403)

	return render_template("sub/create_hole.html", v=v, cost=HOLE_COST)

@app.post("/create_hole")
@is_not_permabanned
def create_sub2(v):
	if not v.can_create_hole:
		abort(403)

	name = request.values.get('name')
	if not name: abort(400)
	name = name.strip().lower()

	if not valid_sub_regex.fullmatch(name):
		return render_template("sub/create_hole.html", v=v, cost=HOLE_COST, error=f"{HOLE_NAME.capitalize()} name not allowed."), 400

	sub = get_sub_by_name(name, graceful=True)
	if not sub:
		if v.coins < HOLE_COST:
			return render_template("sub/create_hole.html", v=v, cost=HOLE_COST, error="You don't have enough coins!"), 403

		v.coins -= HOLE_COST
		g.db.add(v)
		if v.shadowbanned: return {"error": "Internal Server Error"}, 500

		sub = Sub(name=name)
		g.db.add(sub)
		g.db.flush()
		mod = Mod(user_id=v.id, sub=sub.name)
		g.db.add(mod)

		admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_CREATION'], User.id != v.id).all()]
		for admin in admins:
			send_repeatable_notification(admin, f":!marseyparty: /h/{sub} has been created by @{v.username} :marseyparty:")

	return redirect(f'/h/{sub}')

@app.post("/kick/<pid>")
@is_not_permabanned
def kick(v, pid):
	post = get_post(pid)

	if not post.sub: abort(403)
	if not v.mods(post.sub): abort(403)
	if v.shadowbanned: return {"error": "Internal Server Error"}, 500

	old = post.sub
	post.sub = None
	
	if v.admin_level >= PERMS['HOLE_GLOBAL_MODERATION'] and v.id != post.author_id:
		old_str = f'<a href="/h/{old}">/h/{old}</a>'
		ma = ModAction(
			kind='move_hole',
			user_id=v.id,
			target_submission_id=post.id,
			_note=f'{old_str} → main feed',
		)
		g.db.add(ma)
	else:
		ma = SubAction(
			sub=old,
			kind='kick_post',
			user_id=v.id,
			target_submission_id=post.id
		)
		g.db.add(ma)

	if v.id != post.author_id:
		if v.admin_level >= PERMS['HOLE_GLOBAL_MODERATION']: position = 'Admin'
		else: position = 'Mod'
		message = f"@{v.username} ({position}) has moved [{post.title}]({post.shortlink}) from /h/{old} to the main feed!"
		send_repeatable_notification(post.author_id, message)

	g.db.add(post)

	cache.delete_memoized(frontlist)

	return {"message": f"Post kicked from /h/{old} successfully!"}

@app.get('/h/<sub>/settings')
@is_not_permabanned
def sub_settings(v, sub):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub)


@app.post('/h/<sub>/sidebar')
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def post_sub_sidebar(v, sub):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	sub.sidebar = request.values.get('sidebar', '').strip()[:10000]
	sub.sidebar_html = sanitize(sub.sidebar)
	if len(sub.sidebar_html) > 20000: return "Sidebar is too big!"

	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='edit_sidebar',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')


@app.post('/h/<sub>/css')
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def post_sub_css(v, sub):
	sub = get_sub_by_name(sub)
	css = request.values.get('css', '').strip()

	if not sub: abort(404)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	if len(css) > 6000:
		error = "CSS is too long (max 6000 characters)"
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error)

	valid, error = validate_css(css)
	if not valid:
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error)

	sub.css = css
	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='edit_css',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')


@app.get("/h/<sub>/css")
def get_sub_css(sub):
	sub = g.db.query(Sub.css).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	resp=make_response(sub.css or "")
	resp.headers.add("Content-Type", "text/css")
	return resp


@app.post("/h/<sub>/banner")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def sub_banner(v, sub):
	if request.headers.get("cf-ipcountry") == "T1": return {"error":"Image uploads are not allowed through TOR."}, 403

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, patron=v.patron)

	if bannerurl:
		if sub.bannerurl and '/images/' in sub.bannerurl:
			fpath = '/images/' + sub.bannerurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.bannerurl = bannerurl
		g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='change_banner',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.post("/h/<sub>/sidebar_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def sub_sidebar(v, sub):
	if request.headers.get("cf-ipcountry") == "T1": return {"error":"Image uploads are not allowed through TOR."}, 403

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')
	
	file = request.files["sidebar"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	sidebarurl = process_image(name, patron=v.patron)

	if sidebarurl:
		if sub.sidebarurl and '/images/' in sub.sidebarurl:
			fpath = '/images/' + sub.sidebarurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.sidebarurl = sidebarurl
		g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='change_sidebar_image',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.post("/h/<sub>/marsey_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def sub_marsey(v, sub):
	if request.headers.get("cf-ipcountry") == "T1": return {"error":"Image uploads are not allowed through TOR."}, 403

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')
	
	file = request.files["marsey"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	marseyurl = process_image(name, patron=v.patron)

	if marseyurl:
		if sub.marseyurl and '/images/' in sub.marseyurl:
			fpath = '/images/' + sub.marseyurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.marseyurl = marseyurl
		g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='change_marsey',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.get("/holes")
@auth_required
def subs(v):
	subs = g.db.query(Sub, func.count(Submission.sub)).outerjoin(Submission, Sub.name == Submission.sub).group_by(Sub.name).order_by(func.count(Submission.sub).desc()).all()
	return render_template('sub/subs.html', v=v, subs=subs)

@app.post("/hole_pin/<pid>")
@is_not_permabanned
def hole_pin(v, pid):
	p = get_post(pid)

	if not p.sub: abort(403)

	if not v.mods(p.sub): abort(403)

	p.hole_pinned = v.username
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (Mod) has pinned [{p.title}]({p.shortlink}) in /h/{p.sub}"
		send_repeatable_notification(p.author_id, message)

	ma = SubAction(
		sub=p.sub,
		kind='pin_post',
		user_id=v.id,
		target_submission_id=p.id
	)
	g.db.add(ma)

	return {"message": f"Post pinned to /h/{p.sub} successfully!"}

@app.post("/hole_unpin/<pid>")
@is_not_permabanned
def hole_unpin(v, pid):
	p = get_post(pid)

	if not p.sub: abort(403)

	if not v.mods(p.sub): abort(403)

	p.hole_pinned = None
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (Mod) has unpinned [{p.title}]({p.shortlink}) in /h/{p.sub}"
		send_repeatable_notification(p.author_id, message)

	ma = SubAction(
		sub=p.sub,
		kind='unpin_post',
		user_id=v.id,
		target_submission_id=p.id
	)
	g.db.add(ma)

	return {"message": f"Post unpinned from /h/{p.sub} successfully!"}


@app.post('/h/<sub>/stealth')
@is_not_permabanned
def sub_stealth(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == 'braincels': abort(403)
	if not v.mods(sub.name): abort(403)

	sub.stealth = not sub.stealth
	g.db.add(sub)

	cache.delete_memoized(frontlist)

	if sub.stealth:
		ma = SubAction(
			sub=sub.name,
			kind='enable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been enabled for /h/{sub} successfully!"}
	else:
		ma = SubAction(
			sub=sub.name,
			kind='disable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been disabled for /h/{sub} successfully!"}


@app.post("/mod_pin/<cid>")
@is_not_permabanned
def mod_pin(cid, v):
	if not FEATURES['PINS']:
		abort(403)
	comment = get_comment(cid, v=v)
	
	if not comment.stickied:
		if not (comment.post.sub and v.mods(comment.post.sub)): abort(403)
		
		comment.stickied = v.username + " (Mod)"

		g.db.add(comment)

		ma = SubAction(
			sub=comment.post.sub,
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (Mod) has pinned your [comment]({comment.shortlink})!"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}

@app.post("/unmod_pin/<cid>")
@is_not_permabanned
def mod_unpin(cid, v):
	
	comment = get_comment(cid, v=v)
	
	if comment.stickied:
		if not (comment.post.sub and v.mods(comment.post.sub)): abort(403)

		comment.stickied = None
		g.db.add(comment)

		ma = SubAction(
			sub=comment.post.sub,
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (Mod) has unpinned your [comment]({comment.shortlink})!"
			send_repeatable_notification(comment.author_id, message)
	return {"message": "Comment unpinned!"}


@app.get("/h/<sub>/log")
@app.get("/h/<sub>/modlog")
@auth_required
def hole_log(v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	mod = request.values.get("mod")
	if mod: mod_id = get_id(mod)
	else: mod_id = 0

	kind = request.values.get("kind")

	types = ACTIONTYPES

	if kind and kind not in types:
		kind = None
		actions = []
	else:
		actions = g.db.query(SubAction).filter_by(sub=sub.name)

		if mod_id:
			actions = actions.filter_by(user_id=mod_id)
			kinds = set([x.kind for x in actions])
			types2 = {}
			for k,val in types.items():
				if k in kinds: types2[k] = val
			types = types2
		if kind: actions = actions.filter_by(kind=kind)

		actions = actions.order_by(SubAction.id.desc()).offset(25*(page-1)).limit(26).all()
	
	next_exists=len(actions)>25
	actions=actions[:25]
	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(sub=sub.name).all()]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username).all()]

	return render_template("log.html", v=v, admins=mods, types=types, admin=mod, type=kind, actions=actions, next_exists=next_exists, page=page, sub=sub)

@app.get("/h/<sub>/log/<id>")
@auth_required
def hole_log_item(id, v, sub):
	sub = get_sub_by_name(sub)
	if sub.name == "chudrama" and not v.can_see_chudrama: abort(403)
	try: id = int(id)
	except: abort(404)

	action=g.db.get(SubAction, id)

	if not action: abort(404)

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(sub=sub.name).all()]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username).all()]

	types = ACTIONTYPES

	return render_template("log.html", v=v, actions=[action], next_exists=False, page=1, action=action, admins=mods, types=types, sub=sub)
