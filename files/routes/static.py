from files.mail import *
from files.__main__ import app, limiter
from files.helpers.alerts import *
from files.helpers.const import *
from files.helpers.actions import *
from files.classes.award import AWARDS
from sqlalchemy import func, nullslast
import os
from files.classes.mod_logs import ACTIONTYPES, ACTIONTYPES2
from files.classes.badges import BadgeDef
import files.helpers.stats as statshelper
from shutil import move, copyfile


@app.get("/r/drama/comments/<id>/<title>")
@app.get("/r/Drama/comments/<id>/<title>")
def rdrama(id, title):
	id = ''.join(f'{x}/' for x in id)
	return redirect(f'/archives/drama/comments/{id}{title}.html')


@app.get("/marseys")
@auth_required
def marseys(v):
	if SITE == 'rdrama.net':
		marseys = g.db.query(Marsey, User).join(User, Marsey.author_id == User.id).filter(Marsey.submitter_id==None)
		sort = request.values.get("sort", "usage")
		if sort == "usage":
			marseys = marseys.order_by(Marsey.count.desc(), User.username).all()
		elif sort == "added":
			marseys = marseys.order_by(nullslast(Marsey.created_utc.desc()), User.username).all()
		else: # implied sort == "author"
			marseys = marseys.order_by(User.username, Marsey.count.desc()).all()

		original = os.listdir("/asset_submissions/marseys/original")
		for marsey, user in marseys:
			if f'{marsey.name}.png' in original:
				marsey.og = f'{marsey.name}.png'
			elif f'{marsey.name}.webp' in original:
				marsey.og = f'{marsey.name}.webp'
			elif f'{marsey.name}.gif' in original:
				marsey.og = f'{marsey.name}.gif'
			elif f'{marsey.name}.jpeg' in original:
				marsey.og = f'{marsey.name}.jpeg'
	else:
		marseys = g.db.query(Marsey).filter(Marsey.submitter_id==None).order_by(Marsey.count.desc())

	return render_template("marseys.html", v=v, marseys=marseys)

@app.get("/marsey_list.json")
@cache.memoize(timeout=600)
def marsey_list():
	emojis = []

	# From database
	if EMOJI_MARSEYS:
		emojis = [{
			"name": emoji.name,
			"author": author if SITE == 'rdrama.net' or author == "anton-d" else None,
			# yikes, I don't really like this DB schema. Next time be better
			"tags": emoji.tags.split(" ") + [emoji.name[len("marsey"):] \
						if emoji.name.startswith("marsey") else emoji.name],
			"count": emoji.count,
			"class": "Marsey"
		} for emoji, author in g.db.query(Marsey, User.username).join(User, Marsey.author_id == User.id).filter(Marsey.submitter_id==None) \
			.order_by(Marsey.count.desc())]

	# Static shit
	for src in EMOJI_SRCS:
		with open(src, "r", encoding="utf-8") as f:
			emojis = emojis + json.load(f)

	return jsonify(emojis)

@app.get('/sidebar')
@auth_desired
def sidebar(v):
	return render_template('sidebar.html', v=v)


@app.get("/stats")
@auth_required
def participation_stats(v):
	if v.client: return stats_cached()
	return render_template("stats.html", v=v, title="Content Statistics", data=stats_cached())

@cache.memoize(timeout=86400)
def stats_cached():
	return statshelper.stats(SITE_NAME)

@app.get("/chart")
def chart():
	return redirect('/weekly_chart')

@app.get("/weekly_chart")
@auth_required
def weekly_chart(v):
	return send_file(statshelper.chart_path(kind="weekly", site=SITE))

@app.get("/daily_chart")
@auth_required
def daily_chart(v):
	return send_file(statshelper.chart_path(kind="daily", site=SITE))

@app.get("/patrons")
@app.get("/paypigs")
@admin_level_required(PERMS['VIEW_PATRONS'])
def patrons(v):
	if AEVANN_ID and v.id not in (AEVANN_ID, CARP_ID, SNAKES_ID): abort(404)

	users = g.db.query(User).filter(User.patron > 0).order_by(User.patron.desc(), User.id).all()

	return render_template("patrons.html", v=v, users=users, benefactor_def=AWARDS['benefactor'])

@app.get("/admins")
@app.get("/badmins")
@auth_required
def admins(v):
	if v.admin_level >= PERMS['VIEW_SORTED_ADMIN_LIST']:
		admins = g.db.query(User).filter(User.admin_level>1).order_by(User.truecoins.desc()).all()
		admins += g.db.query(User).filter(User.admin_level==1).order_by(User.truecoins.desc()).all()
	else: admins = g.db.query(User).filter(User.admin_level>0).order_by(User.truecoins.desc()).all()
	return render_template("admins.html", v=v, admins=admins)


@app.get("/log")
@app.get("/modlog")
@auth_required
def log(v):

	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	admin = request.values.get("admin")
	if admin: admin_id = get_id(admin)
	else: admin_id = 0

	kind = request.values.get("kind")

	if v and v.admin_level >= PERMS['USER_SHADOWBAN']: types = ACTIONTYPES
	else: types = ACTIONTYPES2

	if kind and kind not in types:
		kind = None
		actions = []
	else:
		actions = g.db.query(ModAction)
		if not (v and v.admin_level >= PERMS['USER_SHADOWBAN']): 
			actions = actions.filter(ModAction.kind.notin_(["shadowban","unshadowban"]))

		if admin_id:
			actions = actions.filter_by(user_id=admin_id)
			kinds = set([x.kind for x in actions])
			kinds.add(kind)
			types2 = {}
			for k,val in types.items():
				if k in kinds: types2[k] = val
			types = types2
		if kind: actions = actions.filter_by(kind=kind)

		actions = actions.order_by(ModAction.id.desc()).offset(25*(page-1)).limit(26).all()
	
	next_exists=len(actions)>25
	actions=actions[:25]
	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(User.username).all()]

	return render_template("log.html", v=v, admins=admins, types=types, admin=admin, type=kind, actions=actions, next_exists=next_exists, page=page)

@app.get("/log/<id>")
@auth_required
def log_item(id, v):
	try: id = int(id)
	except: abort(404)

	action=g.db.get(ModAction, id)

	if not action: abort(404)

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).all()]

	if v and v.admin_level >= PERMS['USER_SHADOWBAN']: types = ACTIONTYPES
	else: types = ACTIONTYPES2

	return render_template("log.html", v=v, actions=[action], next_exists=False, page=1, action=action, admins=admins, types=types)

@app.get("/directory")
@auth_required
def static_megathread_index(v):
	return render_template("megathread_index.html", v=v)

@app.get("/api")
@auth_required
def api(v):
	return render_template("api.html", v=v)

@app.get("/contact")
@app.get("/contactus")
@app.get("/contact_us")
@app.get("/press")
@app.get("/media")
@auth_desired
def contact(v):
	return render_template("contact.html", v=v)

@app.post("/send_admin")
@limiter.limit("1/second;2/minute;6/hour;10/day")
@limiter.limit("1/second;2/minute;6/hour;10/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def submit_contact(v):
	body = request.values.get("message")
	if not body: abort(400)

	if v.is_muted:
		abort(403)

	body = f'This message has been sent automatically to all admins via [/contact](/contact)\n\nMessage:\n\n' + body

	body += process_files()

	body = body.strip()
	
	body_html = sanitize(body)

	new_comment = Comment(author_id=v.id,
						parent_submission=None,
						level=1,
						body_html=body_html,
						sentto=2
						)
	g.db.add(new_comment)
	g.db.flush()
	new_comment.top_comment_id = new_comment.id
	
	admins = g.db.query(User).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL'])
	if SITE == 'watchpeopledie.tv':
		admins = admins.filter(User.id != AEVANN_ID)

	for admin in admins.all():
		notif = Notification(comment_id=new_comment.id, user_id=admin.id)
		g.db.add(notif)



	return render_template("contact.html", v=v, msg="Your message has been sent to the admins!")

@app.get('/archives')
def archivesindex():
	return redirect("/archives/index.html")

@app.get('/archives/<path:path>')
def archives(path):
	resp = make_response(send_from_directory('/archives', path))
	if request.path.endswith('.css'): resp.headers.add("Content-Type", "text/css")
	return resp

def static_file(dir:str, path:str, should_cache:bool, is_webp:bool) -> Response:
	resp = make_response(send_from_directory(dir, path))
	if should_cache:
		resp.headers.remove("Cache-Control")
		resp.headers.add("Cache-Control", "public, max-age=3153600")
	if is_webp:
		resp.headers.remove("Content-Type")
		resp.headers.add("Content-Type", "image/webp")
	return resp

@app.get('/e/<emoji>')
@limiter.exempt
def emoji(emoji):
	if not emoji.endswith('.webp'): abort(404)
	return static_file('assets/images/emojis', emoji, True, True)

@app.get('/i/<path:path>')
@limiter.exempt
def image(path):
	is_webp = path.endswith('.webp')
	return static_file('assets/images', path, is_webp or path.endswith('.gif') or path.endswith('.ttf') or path.endswith('.woff2'), is_webp)

@app.get('/assets/<path:path>')
@app.get('/static/assets/<path:path>')
@limiter.exempt
def static_service(path):
	is_webp = path.endswith('.webp')
	return static_file('assets', path, is_webp or path.endswith('.gif') or path.endswith('.ttf') or path.endswith('.woff2'), is_webp)

### BEGIN FALLBACK ASSET SERVING
# In production, we have nginx serve these locations now.
# These routes stay for local testing. Requests don't reach them on prod.

@app.get('/images/<path>')
@app.get('/hostedimages/<path>')
@app.get("/static/images/<path>")
@limiter.exempt
def images(path):
	return static_file('/images', path, True, True)

@app.get('/videos/<path>')
@limiter.exempt
def videos(path):
	return static_file('/videos', path, True, False)

@app.get('/audio/<path>')
@limiter.exempt
def audio(path):
	return static_file('/audio', path, True, False)

### END FALLBACK ASSET SERVING

@app.get("/robots.txt")
def robots_txt():
	return send_file("assets/robots.txt")

no = (21,22,23,24,25,26,27)

@cache.memoize(timeout=3600)
def badge_list(site):
	badges = g.db.query(BadgeDef).filter(BadgeDef.id.notin_(no)).order_by(BadgeDef.id).all()
	counts_raw = g.db.query(Badge.badge_id, func.count()).group_by(Badge.badge_id).all()
	users = g.db.query(User).count()

	counts = {}
	for c in counts_raw:
		counts[c[0]] = (c[1], float(c[1]) * 100 / max(users, 1))
	
	return badges, counts

@app.get("/badges")
@auth_required
@feature_required('BADGES')
def badges(v):
	badges, counts = badge_list(SITE)
	return render_template("badges.html", v=v, badges=badges, counts=counts)

@app.get("/blocks")
@admin_level_required(PERMS['USER_BLOCKS_VISIBLE'])
def blocks(v):
	blocks=g.db.query(UserBlock).all()
	users = []
	targets = []
	for x in blocks:
		acc_user = get_account(x.user_id)
		acc_tgt = get_account(x.target_id)
		if acc_user.shadowbanned or acc_tgt.shadowbanned: continue
		users.append(acc_user)
		targets.append(acc_tgt)

	return render_template("blocks.html", v=v, users=users, targets=targets)

@app.get("/banned")
@auth_required
def banned(v):
	users = g.db.query(User).filter(User.is_banned > 0, User.unban_utc == 0).all()
	return render_template("banned.html", v=v, users=users)

@app.get("/formatting")
@auth_required
def formatting(v):
	return render_template("formatting.html", v=v)

@app.get("/service-worker.js")
def serviceworker():
	with open("files/assets/js/service-worker.js", "r", encoding="utf-8") as f:
		return Response(f.read(), mimetype='application/javascript')

@app.get("/settings/security")
@auth_required
def settings_security(v):
	return render_template("settings_security.html",
						v=v,
						mfa_secret=pyotp.random_base32() if not v.mfa_secret else None
						)


@app.post("/dismiss_mobile_tip")
def dismiss_mobile_tip():
	session["tooltip_last_dismissed"] = int(time.time())
	return "", 204

@app.get("/transfers/<id>")
@auth_required
def transfers_id(id, v):

	try: id = int(id)
	except: abort(404)

	transfer = g.db.get(Comment, id)

	if not transfer: abort(404)

	return render_template("transfers.html", v=v, page=1, comments=[transfer], standalone=True, next_exists=False)

@app.get("/transfers")
@auth_required
def transfers(v):

	comments = g.db.query(Comment).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_submission == None, Comment.body_html.like("%</a> has transferred %")).order_by(Comment.id.desc())

	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	comments = comments.offset(25 * (page - 1)).limit(26).all()
	next_exists = len(comments) > 25
	comments = comments[:25]

	if v.client:
		return {"data": [x.json for x in comments]}
	else:
		return render_template("transfers.html", v=v, page=page, comments=comments, standalone=True, next_exists=next_exists)


if not os.path.exists(f'files/templates/donate_{SITE_NAME}.html'):
	copyfile(f'files/templates/donate_rDrama.html', f'files/templates/donate_{SITE_NAME}.html')

@app.get('/donate')
@auth_required
def donate(v):
	if v.truecoins < 1000: abort(404)
	return render_template(f'donate_{SITE_NAME}.html', v=v)


if SITE == 'pcmemes.net':
	from files.classes.streamers import *

	id_regex = re.compile('"externalId":"([^"]*?)"', flags=re.A)
	live_regex = re.compile('playerOverlayVideoDetailsRenderer":\{"title":\{"simpleText":"(.*?)"\},"subtitle":\{"runs":\[\{"text":"(.*?)"\},\{"text":" • "\},\{"text":"(.*?)"\}', flags=re.A)
	live_thumb_regex = re.compile('\{"thumbnail":\{"thumbnails":\[\{"url":"(.*?)"', flags=re.A)
	offline_regex = re.compile('","title":"(.*?)".*?"width":48,"height":48\},\{"url":"(.*?)"', flags=re.A)
	offline_details_regex = re.compile('simpleText":"Streamed ([0-9]*?) ([^"]*?)"\},"viewCountText":\{"simpleText":"([0-9.]*?) views"', flags=re.A)

	def process_streamer(id, live='live'):
		url = f'https://www.youtube.com/channel/{id}/{live}'
		req = requests.get(url, cookies={'CONSENT': 'YES+1'}, timeout=5)
		text = req.text
		if '"videoDetails":{"videoId"' in text:
			y = live_regex.search(text)
			count = y.group(3)

			if count == '1 watching now':
				count = "1"

			if 'waiting' in count:
				if live != '':
					return process_streamer(id, '')
				else:
					return None

			count = int(count.replace(',', ''))

			t = live_thumb_regex.search(text)

			thumb = t.group(1)
			name = y.group(2)
			title = y.group(1)
			
			return (True, (id, req.url, thumb, name, title, count))
		else:
			t = offline_regex.search(text)
			if not t:
				if live != '':
					return process_streamer(id, '')
				else:
					return None

			y = offline_details_regex.search(text)

			if y:
				views = y.group(3).replace(',', '')
				quantity = int(y.group(1))
				unit = y.group(2)

				if unit.startswith('second'):
					modifier = 1/60
				elif unit.startswith('minute'):
					modifier = 1
				elif unit.startswith('hour'):
					modifier = 60
				elif unit.startswith('day'):
					modifier = 1440
				elif unit.startswith('week'):
					modifier = 10080
				elif unit.startswith('month'):
					modifier = 43800
				elif unit.startswith('year'):
					modifier = 525600

				minutes = quantity * modifier

				actual = f'{quantity} {unit}'
			else:
				minutes = 9999999999
				actual = '???'
				views = 0

			thumb = t.group(2)

			name = t.group(1)

			return (False, (id, req.url.rstrip('/live'), thumb, name, minutes, actual, views))


	def live_cached():
		live = []
		offline = []
		db = db_session()
		streamers = [x[0] for x in db.query(Streamer.id).all()]
		db.close()
		for id in streamers:
			processed = process_streamer(id)
			if processed:
				if processed[0]: live.append(processed[1])
				else: offline.append(processed[1])

		live = sorted(live, key=lambda x: x[5], reverse=True)
		offline = sorted(offline, key=lambda x: x[4])

		if live: cache.set('live', live)
		if offline: cache.set('offline', offline)


	@app.get('/live')
	@app.get('/logged_out/live')
	@auth_desired_with_logingate
	def live_list(v):
		live = cache.get('live') or []
		offline = cache.get('offline') or []

		return render_template('live.html', v=v, live=live, offline=offline)

	@app.post('/live/add')
	@admin_level_required(PERMS['STREAMERS_MODERATION'])
	def live_add(v):
		link = request.values.get('link').strip()

		if 'youtube.com/channel/' in link:
			id = link.split('youtube.com/channel/')[1].rstrip('/')
		else:
			text = requests.get(link, cookies={'CONSENT': 'YES+1'}, timeout=5).text
			try: id = id_regex.search(text).group(1)
			except: abort(400, "Invalid ID")

		live = cache.get('live') or []
		offline = cache.get('offline') or []

		if not id or len(id) != 24:
			abort(400, "Invalid ID")

		existing = g.db.get(Streamer, id)
		if not existing:
			streamer = Streamer(id=id)
			g.db.add(streamer)
			g.db.flush()
			if v.id != KIPPY_ID:
				send_repeatable_notification(KIPPY_ID, f"@{v.username} (Admin) has added a [new YouTube channel](https://www.youtube.com/channel/{streamer.id})")

			processed = process_streamer(id)
			if processed:
				if processed[0]: live.append(processed[1])
				else: offline.append(processed[1])

		live = sorted(live, key=lambda x: x[5], reverse=True)
		offline = sorted(offline, key=lambda x: x[4])

		if live: cache.set('live', live)
		if offline: cache.set('offline', offline)

		return redirect('/live')

	@app.post('/live/remove')
	@admin_level_required(PERMS['STREAMERS_MODERATION'])
	def live_remove(v):
		id = request.values.get('id').strip()
		if not id: abort(400)
		streamer = g.db.get(Streamer, id)
		if streamer:
			if v.id != KIPPY_ID:
				send_repeatable_notification(KIPPY_ID, f"@{v.username} (Admin) has removed a [YouTube channel](https://www.youtube.com/channel/{streamer.id})")
			g.db.delete(streamer)

		live = cache.get('live') or []
		offline = cache.get('offline') or []

		live = [x for x in live if x[0] != id]
		offline = [x for x in offline if x[0] != id]

		if live: cache.set('live', live)
		if offline: cache.set('offline', offline)

		return redirect('/live')
