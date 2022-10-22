from files.__main__ import app, limiter
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.regex import *
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
@feature_required('AWARDS')
def shop(v):
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
@limiter.limit("100/minute;200/hour;1000/day")
@auth_required
@feature_required('BADGES')
def buy(v, award):
	

	if award == 'benefactor' and not request.values.get("mb"):
		abort(403, "You can only buy the Benefactor award with marseybux.")

	if award == 'ghost' and v.admin_level < PERMS['BUY_GHOST_AWARD']:
		abort(403, "Only admins can buy this award")

	AWARDS = deepcopy(AWARDS2)

	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if award not in AWARDS: abort(400)
	og_price = AWARDS[award]["price"]

	award_title = AWARDS[award]['title']
	price = int(og_price * v.discount)

	if request.values.get("mb"):
		if award == "grass":
			abort(403, "You can't buy the grass award with marseybux.")

		charged = v.charge_account('procoins', price)
		if not charged:
			abort(400, "Not enough marseybux.")
	else:
		charged = v.charge_account('coins', price)
		if not charged:
			abort(400, "Not enough coins.")

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
		for i in range(5): # five items per lootbox
			lb_award = random.choice(["haunt", "stab", "spiders", "fog", "flashlight", "candy-corn", "ectoplasm", "bones", "pumpkin", "jumpscare", "hw-bite", "hw-vax"])
			lootbox_items.append(AWARDS[lb_award]['title'])
			lb_award = AwardRelationship(user_id=v.id, kind=lb_award)
			g.db.add(lb_award)
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

	if CARP_ID and award == "hw-vax":
		u_carp = get_account(CARP_ID)
		currency = 'procoins' if request.values.get("mb") else 'coins'
		u_carp.pay_account(currency, 100)

	if CARP_ID and v.id != CARP_ID and og_price >= 10000:
		send_repeatable_notification(CARP_ID, f"@{v.username} has bought a `{award_title}` award!")


	return {"message": f"{award_title} award bought!"}

@app.post("/trick-or-treat")
@limiter.limit("1/hour", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def trick_or_treat(v):
	
	result = random.choice([0,1])

	if result == 0:
		message = "Trick!"
	else:
		AWARDS = deepcopy(AWARDS2)
		award = random.choice(["haunt", "stab", "spiders", "fog", "flashlight", "candy-corn", "ectoplasm", "bones", "pumpkin", "jumpscare", "hw-bite", "hw-vax"])
		award_title = AWARDS[award]['title']
		award_object = AwardRelationship(user_id=v.id, kind=award)
		g.db.add(award_object)

		g.db.add(v)
		message = f"Treat! You got a {award_title} award!"
	
	return {"message": f"{message}", "result": f"{result}"}

@app.post("/jumpscare")
@auth_required
def execute_jumpscare(v):

	if v.jumpscare > 0:
		v.jumpscare -= 1
		g.db.add(v)
				
	return {}

@app.post("/award/<thing_type>/<id>")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@is_not_permabanned
@feature_required('BADGES')
def award_thing(v, thing_type, id):
	if thing_type == 'post': thing = get_post(id)
	else: thing = get_comment(id)

	if v.shadowbanned: abort(500)
	
	kind = request.values.get("kind", "").strip()
	
	AWARDS = deepcopy(AWARDS2)
	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if kind not in AWARDS: abort(404, "This award doesn't exist")

	award = g.db.query(AwardRelationship).filter(
		AwardRelationship.kind == kind,
		AwardRelationship.user_id == v.id,
		AwardRelationship.submission_id == None,
		AwardRelationship.comment_id == None
	).first()

	if not award: abort(404, "You don't have that award")

	if thing_type == 'post': award.submission_id = thing.id
	else: award.comment_id = thing.id
	award.awarded_utc = int(time.time())

	g.db.add(award)

	note = request.values.get("note", "").strip()

	author = thing.author
	if author.shadowbanned: abort(404)

	if SITE == 'rdrama.net' and author.id in (PIZZASHILL_ID,):
		abort(403, "This user is immune to awards.")

	if kind == "benefactor" and author.id == v.id:
		abort(400, "You can't use this award on yourself.")

	if kind == 'marsify' and author.marsify == 1:
		abort(403, "User is already permanently marsified!")

	if v.id != author.id:
		safe_username = "👻" if thing.ghost else f"@{author.username}"
		
		if author.deflector and v.deflector:
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award but it was deflected on them, they also had a deflector up, so it bounced back and forth until it vaporized!"
			send_repeatable_notification(author.id, msg)

			msg = f"{safe_username} is under the effect of a deflector award; your {AWARDS[kind]['title']} Award has been deflected back to you but your deflector protected you, the award bounced back and forth until it vaporized!"
			send_repeatable_notification(v.id, msg)

			g.db.delete(award)

			return {"message": f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"}

		if author.deflector and v.id != AEVANN_ID and (AWARDS[kind]['price'] > 500 or kind == 'marsify' or kind.istitle()) and kind not in ('pin','unpin','benefactor'):
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award but it was deflected and applied to them :marseytroll:"
			send_repeatable_notification(author.id, msg)
			msg = f"{safe_username} is under the effect of a deflector award; your {AWARDS[kind]['title']} Award has been deflected back to you :marseytroll:"
			send_repeatable_notification(v.id, msg)
			author = v
		elif kind != 'spider':
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
	elif kind == "unban":
		if not author.is_suspended or not author.unban_utc or time.time() > author.unban_utc: abort(403)

		if author.unban_utc - time.time() > 86400:
			author.unban_utc -= 86400
			send_repeatable_notification(author.id, "Your ban duration has been reduced by 1 day!")
		else:
			author.unban_utc = 0
			author.is_banned = 0
			author.ban_reason = None
			send_repeatable_notification(author.id, "You have been unbanned!")
	elif kind == "grass":
		author.is_banned = AUTOJANNY_ID
		author.ban_reason = f"grass award used by @{v.username} on /{thing_type}/{thing.id}"
		author.unban_utc = int(time.time()) + 30 * 86400
		send_repeatable_notification(author.id, f"Your account has been banned permanently for {link}. You must [provide the admins](/contact) a timestamped picture of you touching grass/snow/sand/ass to get unbanned!")
	elif kind == "pin":
		if not FEATURES['PINS']:
			abort(403)
		if thing.stickied and thing.stickied_utc:
			thing.stickied_utc += 3600
		else:
			thing.stickied = f'{v.username} (pin award)'
			if thing_type == 'comment':
				thing.stickied_utc = int(time.time()) + 3600*6
			else:
				thing.stickied_utc = int(time.time()) + 3600
		g.db.add(thing)
		cache.delete_memoized(frontlist)
	elif kind == "unpin":
		if not thing.stickied_utc: abort(403)

		if thing_type == 'comment':
			t = thing.stickied_utc - 3600*6
		else:
			t = thing.stickied_utc - 3600

		if time.time() > t:
			thing.stickied = None
			thing.stickied_utc = None
			cache.delete_memoized(frontlist)
		else: thing.stickied_utc = t
		g.db.add(thing)
	elif kind == "agendaposter" and not (author.agendaposter and author.agendaposter == 0):
		if author.marseyawarded:
			abort(409, "This user is under the effect of a conflicting award: Marsey award.")

		if author.agendaposter and time.time() < author.agendaposter: author.agendaposter += 86400
		else: author.agendaposter = int(time.time()) + 86400
		
		badge_grant(user=author, badge_id=28)
	elif kind == "flairlock":
		if thing.ghost: abort(403)
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
		badge_grant(badge_id=68, user=author)
	elif kind == "unpausable":
		badge_grant(badge_id=67, user=author)
	elif kind == "marsey":
		if author.marseyawarded: author.marseyawarded += 86400
		else: author.marseyawarded = int(time.time()) + 86400
		badge_grant(user=author, badge_id=98)
	elif kind == "pizzashill":
		if author.bird:
			abort(409, "This user is under the effect of a conflicting award: Bird Site award.")
		if author.longpost: author.longpost += 86400
		else: author.longpost = int(time.time()) + 86400
		badge_grant(user=author, badge_id=97)
	elif kind == "bird":
		if author.longpost:
			abort(409, "This user is under the effect of a conflicting award: Pizzashill award.")
		if author.bird: author.bird += 86400
		else: author.bird = int(time.time()) + 86400
		badge_grant(user=author, badge_id=95)
	elif kind == "eye":
		badge_grant(badge_id=83, user=author)
	elif kind == "offsitementions":
		badge_grant(user=author, badge_id=140)
	elif kind == "alt":
		badge_grant(badge_id=84, user=author)
	elif kind == "unblockable":
		badge_grant(badge_id=87, user=author)
		for block in g.db.query(UserBlock).filter_by(target_id=author.id).all(): g.db.delete(block)
	elif kind == "fish":
		badge_grant(badge_id=90, user=author)
	elif kind == "progressivestack":
		if not FEATURES['PINS']:
			abort(403)
		if author.progressivestack: author.progressivestack += 21600
		else: author.progressivestack = int(time.time()) + 21600
		badge_grant(user=author, badge_id=94)
	elif kind == "benefactor":
		if author.patron: abort(409, f"This user is already a {patron.lower()}!")
		author.patron = 1
		if author.patron_utc: author.patron_utc += 2629746
		else: author.patron_utc = int(time.time()) + 2629746
		author.procoins += 2500
		badge_grant(user=v, badge_id=103)
	elif kind == "rehab":
		if author.rehab: author.rehab += 86400
		else: author.rehab = int(time.time()) + 86400
		badge_grant(user=author, badge_id=109)
	elif kind == "deflector":
		author.deflector = int(time.time()) + 36000
	elif kind == "beano":
		badge_grant(user=author, badge_id=128)
	elif kind == "checkmark":
		author.verified = "Verified"
		badge_grant(user=author, badge_id=150)
	elif kind == 'marsify':
		if not author.marsify or author.marsify != 1:
			if author.marsify: author.marsify += 21600
			else: author.marsify = int(time.time()) + 21600
		badge_grant(user=author, badge_id=170)

		if thing_type == 'comment' and (not author.deflector or v.id == AEVANN_ID):
			body = thing.body
			if author.owoify: body = owoify(body)
			body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)
	elif "Vampire" in kind and kind == v.house:
		if author.bite: author.bite += 86400
		else: author.bite = int(time.time()) + 86400
		
		if not author.old_house:
			author.old_house = author.house
		
		if 'Vampire' not in author.house:
			author.house = 'Vampire'

		badge_grant(user=author, badge_id=168)
	elif "Racist" in kind and kind == v.house:
		if author.earlylife: author.earlylife += 86400
		else: author.earlylife = int(time.time()) + 86400
		badge_grant(user=author, badge_id=169)
	elif ("Furry" in kind and kind == v.house) or kind == 'owoify':
		if author.owoify: author.owoify += 21600
		else: author.owoify = int(time.time()) + 21600
		badge_grant(user=author, badge_id=167)

		if thing_type == 'comment' and not (author.deflector or v.id == AEVANN_ID):
			body = thing.body
			body = owoify(body)
			if author.marsify: body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)
	elif ("Femboy" in kind and kind == v.house) or kind == 'rainbow':
		if author.rainbow: author.rainbow += 86400
		else: author.rainbow = int(time.time()) + 86400
		badge_grant(user=author, badge_id=171)
	elif kind == "spider":
		if author.spider: author.spider += 86400
		else: author.spider = int(time.time()) + 86400
		badge_grant(user=author, badge_id=179, notify=False)
	elif kind == "hw-bite":
		if author.homoween_zombie == 'ZOMBIE':
			author = v

		if author.homoween_zombie == 'HEALTHY':
			author.homoween_zombie = 'ZOMBIE'

			award_object = AwardRelationship(user_id=author.id, kind='hw-bite')
			g.db.add(award_object)
			badge_grant(user=author, badge_id=181)

		elif author.homoween_zombie == 'VAXXED':
			author.homoween_zombie = 'HEALTHY'
			send_repeatable_notification(author.id, "You are no longer **VAXXMAXXED**! Time for another booster!")

			badge = author.has_badge(182)
			if badge: g.db.delete(badge)
	elif kind == "hw-vax" and author.id != v.id:
		if author.homoween_zombie == 'ZOMBIE':
				author.homoween_zombie = 'HEALTHY'
				send_repeatable_notification(author.id, "You are no longer **INFECTED**! Praise Fauci!")

				badge = author.has_badge(181)
				if badge: g.db.delete(badge)
		elif author.homoween_zombie == 'HEALTHY':
			author.homoween_zombie = 'VAXXED'

			badge_grant(user=author, badge_id=182)
	elif kind == "jumpscare":
		author.jumpscare += 1
		
	elif kind == "hw-grinch":
		badge_grant(user=author, badge_id=185)

	if author.received_award_count: author.received_award_count += 1
	else: author.received_award_count = 1
	g.db.add(author)

	return {"message": f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"}
