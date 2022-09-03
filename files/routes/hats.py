from files.__main__ import app
from files.classes.hats import *
from files.helpers.alerts import *
from files.helpers.wrappers import *
from files.helpers.const import *
from files.helpers.actions import *
from flask import g

@app.get("/hats")
@auth_required
def hats(v):
	if not FEATURES['HATS']: abort(404)

	owned_hats = [x[0] for x in g.db.query(Hat.hat_id).filter_by(user_id=v.id).all()]
	owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.id.in_(owned_hats)).order_by(HatDef.price, HatDef.name).all()
	not_owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.id.notin_(owned_hats)).order_by(HatDef.price, HatDef.name).all()

	return render_template("hats.html", owned=owned, not_owned=not_owned, v=v)

@app.post("/buy_hat/<hat_id>")
@auth_required
def buy_hat(v, hat_id):
	if not FEATURES['HATS']: abort(404)

	try: hat_id = int(hat_id)
	except: return {"error": "Hat not found!"}

	hat = g.db.query(HatDef).filter_by(id=hat_id).one_or_none()
	if not hat: return {"error": "Hat not found!"}

	if request.values.get("mb"):
		if v.procoins < hat.price: return {"error": "Not enough marseybux."}, 400
		v.procoins -= hat.price
		hat.author.procoins = hat.price * 0.05
		currency = "marseybux"
	else:
		if v.coins < hat.price: return {"error": "Not enough coins."}, 400
		v.coins -= hat.price
		v.coins_spent_on_hats += hat.price
		hat.author.coins = hat.price * 0.05
		currency = "coins"

	new_hat = Hat(user_id=v.id, hat_id=hat.id)
	g.db.add(new_hat)

	g.db.add(v)
	g.db.add(hat.author)

	if v.id != hat.author.id:
		send_repeatable_notification(
			hat.author.id,
			f":marseycapitalistmanlet: @{v.username} has just bought `{hat.name}`, you have received your %5 cut ({int(hat.price * 0.05)} {currency}) :!marseycapitalistmanlet:"
		)

	if v.num_of_hats_bought >= 249:
		badge_grant(user=v, badge_id=154)
	elif v.num_of_hats_bought >= 99:
		badge_grant(user=v, badge_id=153)
	elif v.num_of_hats_bought >= 24:
		badge_grant(user=v, badge_id=152)

	return {"message": "Hat bought!"}


@app.post("/equip_hat/<hat_id>")
@auth_required
def equip_hat(v, hat_id):
	if not FEATURES['HATS']: abort(404)

	try: hat_id = int(hat_id)
	except: return {"error": "Hat not found!"}

	hat = g.db.query(Hat).filter_by(hat_id=hat_id, user_id=v.id).one_or_none()
	if not hat: return {"error": "You don't own this hat!"}

	v.equipped_hat_id = hat_id
	g.db.add(v)

	return {"message": "Hat equipped!"}

@app.post("/unequip_hat")
@auth_required
def unequip_hat(v):
	if not FEATURES['HATS']: abort(404)

	v.equipped_hat_id = None
	g.db.add(v)

	return {"message": "Hat unequipped!"}