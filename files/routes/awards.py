from files.__main__ import app, limiter
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.regex import *
from files.helpers.discord import *
from files.helpers.actions import *
from files.classes.award import *
from .front import frontlist
from flask import g, request
from files.helpers.sanitize import filter_emojis_only
from files.helpers.marsify import marsify
from files.helpers.owoify import owoify
from copy import deepcopy

@app.get("/shop")
@app.get("/settings/shop")
@auth_required
def shop(v):
	if not FEATURES['AWARDS']:
		abort(404)

	AWARDS = deepcopy(AWARDS2)

	if v.house:
		AWARDS[v.house] = deepcopy(HOUSE_AWARDS[v.house])

	for val in AWARDS.values(): val["owned"] = 0

	for useraward in g.db.query(AwardRelationship).filter(AwardRelationship.user_id == v.id, AwardRelationship.submission_id == None, AwardRelationship.comment_id == None).all():
		if useraward.kind in AWARDS: AWARDS[useraward.kind]["owned"] += 1

	for val in AWARDS.values():
		val["baseprice"] = int(val["price"])
		if val["kind"].endswith('Founder'):
			val["baseprice"] = int(val["baseprice"] / 0.75)
		val["price"] = int(val["price"] * v.discount)

	sales = g.db.query(func.sum(User.coins_spent)).scalar()
	return render_template("shop.html", awards=list(AWARDS.values()), v=v, sales=sales)


@app.post("/buy/<award>")
@auth_required
def buy(v, award):
	if not FEATURES['AWARDS']:
		abort(404)

	if award == 'benefactor' and not request.values.get("mb"):
		return {"error": "You can only buy the Benefactor award with marseybux."}, 403

	if award == 'ghost' and v.admin_level < 2:
		return {"error": "Only admins can buy this award."}, 403

	AWARDS = deepcopy(AWARDS2)

	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if award not in AWARDS: abort(400)
	og_price = AWARDS[award]["price"]

	price = int(og_price * v.discount)

	if request.values.get("mb"):
		if v.procoins < price: return {"error": "Not enough marseybux."}, 400
		if award == "grass": return {"error": "You can't buy the grass award with marseybux."}, 403
		v.procoins -= price
	else:
		if v.coins < price: return {"error": "Not enough coins."}, 400
		v.coins -= price
		v.coins_spent += price
		if v.coins_spent >= 1000000:
			badge_grant(badge_id=73, user=v)
		elif v.coins_spent >= 500000:
			badge_grant(badge_id=72, user=v)
		elif v.coins_spent >= 250000:
			
			badge_grant(badge_id=71, user=v)
		elif v.coins_spent >= 100000:
			badge_grant(badge_id=70, user=v)
		elif v.coins_spent >= 10000:
			badge_grant(badge_id=69, user=v)
		g.db.add(v)


	if award == "lootbox":
		lootbox_items = []
		for i in [1,2,3,4,5]:
			award = random.choice(["firework", "confetti", "ricardo", "wholesome", "shit", "fireflies", "scooter", "train"])
			lootbox_items.append(AWARDS[award]['title'])
			award = AwardRelationship(user_id=v.id, kind=award)
			g.db.add(award)
			g.db.flush()

		v.lootboxes_bought += 1
		lootbox_msg = "You open your lootbox and receive: " + ', '.join(lootbox_items)
		send_repeatable_notification(v.id, lootbox_msg)
		
		if v.lootboxes_bought == 10:
			badge_grant(badge_id=76, user=v)
		elif v.lootboxes_bought == 50:
			badge_grant(badge_id=77, user=v)
		elif v.lootboxes_bought == 150:
			badge_grant(badge_id=78, user=v)

	else:
		award_object = AwardRelationship(user_id=v.id, kind=award)
		g.db.add(award_object)

	g.db.add(v)

	if CARP_ID and v.id != CARP_ID and og_price >= 10000:
		send_repeatable_notification(CARP_ID, f"@{v.username} has bought a `{award}` award!")


	return {"message": "Award bought!"}

@app.post("/award/<thing_type>/<id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
def award_thing(v, thing_type, id):
	if not FEATURES['AWARDS']:
		abort(404)

	if thing_type == 'post': thing = get_post(id)
	else: thing = get_comment(id)

	if not thing: return {"error": f"This {thing_type} doesn't exist."}, 404

	if v.shadowbanned: return render_template('errors/500.html', err=True, v=v), 500
	
	kind = request.values.get("kind", "").strip()
	
	AWARDS = deepcopy(AWARDS2)
	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if kind not in AWARDS:
		return {"error": "This award doesn't exist."}, 404

	award = g.db.query(AwardRelationship).filter(
		AwardRelationship.kind == kind,
		AwardRelationship.user_id == v.id,
		AwardRelationship.submission_id == None,
		AwardRelationship.comment_id == None
	).first()

	if not award:
		return {"error": "You don't have that award."}, 404

	if thing_type == 'post': award.submission_id = thing.id
	else: award.comment_id = thing.id
	award.awarded_utc = int(time.time())

	g.db.add(award)

	note = request.values.get("note", "").strip()

	author = thing.author

	if author.id in (PIZZASHILL_ID, DAD_ID) and v.id not in (PIZZASHILL_ID, DAD_ID):
		return {"error": "This user is immune to awards."}, 403

	if kind == "benefactor" and author.id == v.id:
		return {"error": "You can't use this award on yourself."}, 400

	if (kind.startswith('Femboy') or kind == 'marsify') and author.marsify == 1:
		return {"error": "User is already permenantly marsified!"}, 403

	if v.id != author.id:
		if author.deflector and (AWARDS[kind]['price'] > 500 or kind.istitle()) and kind not in ('pin','unpin','benefactor'):
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award but it was deflected and applied to them :marseytroll:"
			send_repeatable_notification(author.id, msg)
			msg = f"@{author.username} is under the effect of a deflector award; your {AWARDS[kind]['title']} Award has been deflected back to you :marseytroll:"
			send_repeatable_notification(v.id, msg)
			author = v
		else:
			msg = f"@{v.username} has given your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award!"
			if note: msg += f"\n\n> {note}"
			send_repeatable_notification(author.id, msg)

	link = f"[this {thing_type}]({thing.shortlink})"

	if kind == "ban":
		if not author.is_suspended:
			author.ban(reason=f"1-Day ban award used by @{v.username} on /{thing_type}/{thing.id}", days=1)
			send_repeatable_notification(author.id, f"Your account has been banned for **a day** for {link}. It sucked and you should feel bad.")
		elif author.unban_utc:
			author.unban_utc += 86400
			send_repeatable_notification(author.id, f"Your account has been banned for **yet another day** for {link}. Seriously man?")

		if v.admin_level > 2:
			log_link = f'/{thing_type}/{thing.id}'
			reason = f'<a href="{log_link}">{log_link}</a>'

			note = f'reason: "{reason}", duration: for 1 day'
			ma=ModAction(
				kind="ban_user",
				user_id=v.id,
				target_user_id=author.id,
				_note=note
				)
			g.db.add(ma)
	elif kind == "unban":
		if not author.is_suspended or not author.unban_utc or time.time() > author.unban_utc: abort(403)

		if author.unban_utc - time.time() > 86400:
			author.unban_utc -= 86400
			send_repeatable_notification(author.id, "Your ban duration has been reduced by 1 day!")
		else:
			author.unban_utc = 0
			author.is_banned = 0
			author.ban_evade = 0
			author.ban_reason = None
			send_repeatable_notification(author.id, "You have been unbanned!")

		if v.admin_level > 2:
			ma=ModAction(
				kind="unban_user",
				user_id=v.id,
				target_user_id=author.id,
				)
			g.db.add(ma)
	elif kind == "grass":
		author.is_banned = AUTOJANNY_ID
		author.ban_reason = f"grass award used by @{v.username} on /{thing_type}/{thing.id}"
		author.unban_utc = int(time.time()) + 30 * 86400
		send_repeatable_notification(author.id, f"Your account has been banned permanently for {link}. You must [provide the admins](/contact) a timestamped picture of you touching grass/snow/sand/ass to get unbanned!")

		if v.admin_level > 2:
			log_link = f'/{thing_type}/{thing.id}'
			reason = f'<a href="{log_link}">{log_link}</a>'

			note = f'reason: "{reason}", duration: for 30 days'
			ma=ModAction(
				kind="ban_user",
				user_id=v.id,
				target_user_id=author.id,
				_note=note
				)
			g.db.add(ma)
	elif kind == "pin":
		if not FEATURES['PINS']:
			abort(403)
		if thing.stickied and thing.stickied_utc:
			thing.stickied_utc += 3600
		else:
			thing.stickied = f'{v.username} (pin award)'
			thing.stickied_utc = int(time.time()) + 3600
		g.db.add(thing)
		cache.delete_memoized(frontlist)
	elif kind == "unpin":
		if not thing.stickied_utc: abort(403)
		t = thing.stickied_utc - 3600
		if time.time() > t:
			thing.stickied = None
			thing.stickied_utc = None
			cache.delete_memoized(frontlist)
		else: thing.stickied_utc = t
		g.db.add(thing)
	elif kind == "agendaposter" and not (author.agendaposter and author.agendaposter == 0):
		if author.marseyawarded:
			return {"error": "This user is the under the effect of a conflicting award: Marsey award."}, 404

		if author.agendaposter and time.time() < author.agendaposter: author.agendaposter += 86400
		else: author.agendaposter = int(time.time()) + 86400
		
		badge_grant(user=author, badge_id=28)
	elif kind == "flairlock":
		new_name = note[:100].replace("𒐪","")
		if not new_name and author.flairchanged:
			author.flairchanged += 86400
		else:
			author.customtitleplain = new_name
			new_name = censor_slurs(new_name, None)
			author.customtitle = filter_emojis_only(new_name)
			if len(author.customtitle) > 1000: abort(403)
			author.flairchanged = int(time.time()) + 86400
			badge_grant(user=author, badge_id=96)
	elif kind == "pause":
		author.mute = True
		badge_grant(badge_id=68, user=author)
	elif kind == "unpausable":
		author.unmutable = True
		badge_grant(badge_id=67, user=author)
	elif kind == "marsey":
		if author.marseyawarded: author.marseyawarded += 86400
		else: author.marseyawarded = int(time.time()) + 86400
		badge_grant(user=author, badge_id=98)
	elif kind == "pizzashill":
		if author.bird:
			return {"error": "This user is the under the effect of a conflicting award: Bird Site award."}, 404
		if author.longpost: author.longpost += 86400
		else: author.longpost = int(time.time()) + 86400
		badge_grant(user=author, badge_id=97)
	elif kind == "bird":
		if author.longpost:
			return {"error": "This user is the under the effect of a conflicting award: Pizzashill award."}, 404
		if author.bird: author.bird += 86400
		else: author.bird = int(time.time()) + 86400
		badge_grant(user=author, badge_id=95)
	elif kind == "eye":
		author.eye = True
		badge_grant(badge_id=83, user=author)
	elif kind == "offsitementions":
		author.offsitementions = True
		badge_grant(user=author, badge_id=140)
	elif kind == "alt":
		author.alt = True
		badge_grant(badge_id=84, user=author)
	elif kind == "unblockable":
		author.unblockable = True
		badge_grant(badge_id=87, user=author)
		for block in g.db.query(UserBlock).filter_by(target_id=author.id).all(): g.db.delete(block)
	elif kind == "fish":
		author.fish = True
		badge_grant(badge_id=90, user=author)
	elif kind == "progressivestack":
		if not FEATURES['PINS']:
			abort(403)
		if author.progressivestack: author.progressivestack += 21600
		else: author.progressivestack = int(time.time()) + 21600
		badge_grant(user=author, badge_id=94)
	elif kind == "benefactor":
		if author.patron: return {"error": "This user is already a paypig!"}, 400
		author.patron = 1
		if author.patron_utc: author.patron_utc += 2629746
		else: author.patron_utc = int(time.time()) + 2629746
		author.procoins += 2500
		if author.discord_id: add_role(author, "1")
		badge_grant(user=v, badge_id=103)
	elif kind == "rehab":
		if author.rehab: author.rehab += 86400
		else: author.rehab = int(time.time()) + 86400
		badge_grant(user=author, badge_id=109)
	elif kind == "deflector":
		if author.deflector: author.deflector += 36000
		else: author.deflector = int(time.time()) + 36000
	elif kind == "beano":
		badge_grant(user=author, badge_id=128)
	elif kind == "checkmark":
		author.verified = "Verified"
		badge_grant(user=author, badge_id=150)
	elif "Vampire" in kind and kind == v.house:
		if author.bite: author.bite += 86400
		else: author.bite = int(time.time()) + 86400
		author.old_house = author.house
		author.house = 'Vampire'
	elif "Racist" in kind and kind == v.house:
		if author.earlylife: author.earlylife += 86400
		else: author.earlylife = int(time.time()) + 86400
	elif ("Furry" in kind and kind == v.house) or kind == 'owoify':
		if author.owoify: author.owoify += 21600
		else: author.owoify = int(time.time()) + 21600

		if thing_type == 'comment' and not author.deflector:
			body = thing.body
			body = owoify(body)
			if author.marsify: body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)
	elif ("Femboy" in kind and kind == v.house) or kind == 'marsify':
		if author.marsify: author.marsify += 21600
		else: author.marsify = int(time.time()) + 21600

		if thing_type == 'comment' and not author.deflector:
			body = thing.body
			if author.owoify: body = owoify(body)
			body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)

	if author.received_award_count: author.received_award_count += 1
	else: author.received_award_count = 1
	g.db.add(author)

	if request.referrer and len(request.referrer) > 1:
		if request.referrer == f'{SITE_FULL}/submit': return redirect(thing.permalink)
		elif request.referrer.startswith(f'{SITE_FULL}/'): return redirect(request.referrer)
	return redirect(SITE_FULL)



@app.get("/admin/awards")
@admin_level_required(2)
def admin_userawards_get(v):
	if not FEATURES['AWARDS']:
		abort(404)

	if SITE == 'pcmemes.net' and v.admin_level < 3: abort(403)

	if v.admin_level != 3:
		return render_template("admin/awards.html", awards=list(AWARDS3.values()), v=v)

	return render_template("admin/awards.html", awards=list(AWARDS.values()), v=v) 

@app.post("/admin/awards")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@admin_level_required(2)
def admin_userawards_post(v):
	if not FEATURES['AWARDS']:
		abort(404)
	
	if SITE == 'pcmemes.net' and v.admin_level < 3: abort(403)

	try: u = request.values.get("username").strip()
	except: abort(404)

	whitelist = ("shit", "fireflies", "train", "scooter", "wholesome", "tilt", "glowie")

	u = get_user(u, graceful=False, v=v)

	notify_awards = {}

	for key, value in request.values.items():
		if key not in AWARDS: continue

		if v.admin_level < 3 and key not in whitelist: continue

		if value:
			
			if int(value) > 100 or (int(value) > 10 and v.id != AEVANN_ID): abort(403)

			if int(value): notify_awards[key] = int(value)

			for x in range(int(value)):
				award = AwardRelationship(
					user_id=u.id,
					kind=key,
					granted=True
				)

				g.db.add(award)

	if v.id != u.id:
		text = f"@{v.username} has given you the following awards:\n\n"
		for key, value in notify_awards.items():
			text += f" - **{value}** {AWARDS[key]['title']} {'Awards' if value != 1 else 'Award'}\n"
		send_repeatable_notification(u.id, text)

	note = ""

	for key, value in notify_awards.items():
		note += f"{value} {AWARDS[key]['title']}, "

	if len(note) > 500: return {"error": "You're giving too many awards at the same time!"}
	
	ma=ModAction(
		kind="grant_awards",
		user_id=v.id,
		target_user_id=u.id,
		_note=note[:-2]
		)
	g.db.add(ma)


	if v.admin_level != 3: return render_template("admin/awards.html", awards=list(AWARDS3.values()), v=v)
	return render_template("admin/awards.html", awards=list(AWARDS.values()), v=v) 

