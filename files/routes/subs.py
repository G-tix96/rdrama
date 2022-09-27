from files.__main__ import app, limiter, mail
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
	try: pid = int(pid)
	except: abort(400)

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

	
	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}



@app.post("/exile/comment/<cid>")
@is_not_permabanned
def exile_comment(v, cid):
	try: cid = int(cid)
	except: abort(400)

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

	
	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}


@app.post("/h/<sub>/unexile/<uid>")
@is_not_permabanned
def unexile(v, sub, uid):
	u = get_account(uid)

	if not v.mods(sub): abort(403)

	if u.exiled_from(sub):
		exile = g.db.query(Exile).filter_by(user_id=u.id, sub=sub).one_or_none()
		g.db.delete(exile)

		send_notification(u.id, f"@{v.username} has revoked your exile from /h/{sub}")

	
	
	if request.headers.get("Authorization") or request.headers.get("xhr"):
		return {"message": f"@{u.username} has been unexiled from /h/{sub} successfully!"}

	
	return redirect(f'/h/{sub}/exilees')







@app.post("/h/<sub>/block")
@auth_required
def block_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	existing = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub).one_or_none()

	if not existing:
		block = SubBlock(user_id=v.id, sub=sub)
		g.db.add(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} blocked successfully!"}


@app.post("/h/<sub>/unblock")
@auth_required
def unblock_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	block = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub).one_or_none()

	if block:
		g.db.delete(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unblocked successfully!"}


@app.post("/h/<sub>/subscribe")
@auth_required
def subscribe_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	existing = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()

	if not existing:
		subscribe = SubJoin(user_id=v.id, sub=sub)
		g.db.add(subscribe)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unblocked successfully!"}

@app.post("/h/<sub>/unsubscribe")
@auth_required
def unsubscribe_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	subscribe = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()

	if subscribe:
		g.db.delete(subscribe)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} blocked successfully!"}

@app.post("/h/<sub>/follow")
@auth_required
def follow_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	existing = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	
	if not existing:
		subscription = SubSubscription(user_id=v.id, sub=sub.name)
		g.db.add(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} followed successfully!"}

@app.post("/h/<sub>/unfollow")
@auth_required
def unfollow_sub(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	subscription = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	
	if subscription:
		g.db.delete(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unfollowed successfully!"}

@app.get("/h/<sub>/mods")
@auth_required
def mods(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	users = g.db.query(User, Mod).join(Mod).filter_by(sub=sub.name).order_by(Mod.created_utc).all()

	return render_template("sub/mods.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/exilees")
@auth_required
def sub_exilees(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	users = g.db.query(User, Exile).join(Exile, Exile.user_id==User.id) \
				.filter_by(sub=sub.name) \
				.order_by(nullslast(Exile.created_utc.desc()), User.username).all()

	return render_template("sub/exilees.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/blockers")
@auth_required
def sub_blockers(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	users = g.db.query(User).join(SubBlock) \
				.filter_by(sub=sub.name) \
				.order_by(nullslast(SubBlock.created_utc.desc()), User.username).all()

	return render_template("sub/blockers.html", 
		v=v, sub=sub, users=users, verb="blocking")


@app.get("/h/<sub>/followers")
@auth_required
def sub_followers(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

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

	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	if not v.mods(sub): abort(403)

	user = request.values.get('user')

	if not user: abort(400)

	user = get_user(user)

	if sub in ('furry','vampire','racist','femboy') and not v.client and not user.house.lower().startswith(sub):
		return {"error": f"@{user.username} needs to be a member of House {sub.capitalize()} to be added as a mod there!"}, 400

	existing = g.db.query(Mod).filter_by(user_id=user.id, sub=sub).one_or_none()

	if not existing:
		mod = Mod(user_id=user.id, sub=sub)
		g.db.add(mod)

		if v.id != user.id:
			send_repeatable_notification(user.id, f"@{v.username} has added you as a mod to /h/{sub}")

	
	return redirect(f'/h/{sub}/mods')


@app.post("/h/<sub>/remove_mod")
@is_not_permabanned
def remove_mod(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	sub = sub.name

	if not v.mods(sub): abort(403)

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

	sub = g.db.query(Sub).filter_by(name=name).one_or_none()
	if not sub:
		if v.coins < HOLE_COST:
			return render_template("sub/create_hole.html", v=v, cost=HOLE_COST, error="You don't have enough coins!"), 403

		v.coins -= HOLE_COST

		g.db.add(v)

		sub = Sub(name=name)
		g.db.add(sub)
		g.db.flush()
		mod = Mod(user_id=v.id, sub=sub.name)
		g.db.add(mod)

		admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level > 1, User.id != v.id).all()]
		for admin in admins:
			send_repeatable_notification(admin, f":!marseyparty: /h/{sub} has been created by @{v.username} :marseyparty:")

	return redirect(f'/h/{sub}')

@app.post("/kick/<pid>")
@is_not_permabanned
def kick(v, pid):
	try: pid = int(pid)
	except: abort(400)

	post = get_post(pid)

	if not post.sub: abort(403)
	if not v.mods(post.sub): abort(403)

	old = post.sub
	post.sub = None
	g.db.add(post)

	cache.delete_memoized(frontlist)

	return {"message": f"Post kicked from /h/{old} successfully!"}

@app.get('/h/<sub>/settings')
@is_not_permabanned
def sub_settings(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	if not v.mods(sub.name): abort(403)

	return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub)


@app.post('/h/<sub>/sidebar')
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def post_sub_sidebar(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	
	if not v.mods(sub.name): abort(403)

	sub.sidebar = request.values.get('sidebar', '').strip()[:10000]
	sub.sidebar_html = sanitize(sub.sidebar)
	if len(sub.sidebar_html) > 20000: return "Sidebar is too big!"

	g.db.add(sub)


	return redirect(f'/h/{sub}/settings')


@app.post('/h/<sub>/css')
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def post_sub_css(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	css = request.values.get('css', '').strip()

	if not sub: abort(404)
	if not v.mods(sub.name): abort(403)

	if len(css) > 6000:
		error = "CSS is too long (max 6000 characters)"
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error)

	valid, error = validate_css(css)
	if not valid:
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error)

	sub.css = css
	g.db.add(sub)

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

	sub = g.db.query(Sub).filter_by(name=sub.lower().strip()).one_or_none()
	if not sub: abort(404)

	if not v.mods(sub.name): abort(403)

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name)

	if bannerurl:
		if sub.bannerurl and '/images/' in sub.bannerurl:
			fpath = '/images/' + sub.bannerurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.bannerurl = bannerurl
		g.db.add(sub)

	return redirect(f'/h/{sub}/settings')

@app.post("/h/<sub>/sidebar_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def sub_sidebar(v, sub):
	if request.headers.get("cf-ipcountry") == "T1": return {"error":"Image uploads are not allowed through TOR."}, 403

	sub = g.db.query(Sub).filter_by(name=sub.lower().strip()).one_or_none()
	if not sub: abort(404)

	if not v.mods(sub.name): abort(403)
	
	file = request.files["sidebar"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	sidebarurl = process_image(name)

	if sidebarurl:
		if sub.sidebarurl and '/images/' in sub.sidebarurl:
			fpath = '/images/' + sub.sidebarurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.sidebarurl = sidebarurl
		g.db.add(sub)

	return redirect(f'/h/{sub}/settings')

@app.post("/h/<sub>/marsey_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def sub_marsey(v, sub):
	if request.headers.get("cf-ipcountry") == "T1": return {"error":"Image uploads are not allowed through TOR."}, 403

	sub = g.db.query(Sub).filter_by(name=sub.lower().strip()).one_or_none()
	if not sub: abort(404)

	if not v.mods(sub.name): abort(403)
	
	file = request.files["marsey"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	marseyurl = process_image(name)

	if marseyurl:
		if sub.marseyurl and '/images/' in sub.marseyurl:
			fpath = '/images/' + sub.marseyurl.split('/images/')[1]
			if path.isfile(fpath): os.remove(fpath)
		sub.marseyurl = marseyurl
		g.db.add(sub)

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

	return {"message": f"Post unpinned from /h/{p.sub} successfully!"}


@app.post('/h/<sub>/stealth')
@is_not_permabanned
def sub_stealth(v, sub):
	sub = g.db.query(Sub).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)

	if sub.name == 'braincels': abort(403)
	if not v.mods(sub.name): abort(403)

	sub.stealth = not sub.stealth
	g.db.add(sub)

	cache.delete_memoized(frontlist)

	if sub.stealth:
		return {"message": f"Stealth mode has been enabled for /h/{sub} successfully!"}
	else:
		return {"message": f"Stealth mode has been disabled for /h/{sub} successfully!"}