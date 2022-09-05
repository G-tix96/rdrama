import json
from files.__main__ import app
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.wrappers import *
from files.helpers.blackjack import *
from files.helpers.slots import *
from files.helpers.lottery import *


@app.get("/casino")
@auth_required
def casino(v):
	participants = get_users_participating_in_lottery()
	return render_template("casino.html", v=v, participants=participants)


@app.post("/casino/slots")
@limiter.limit("3/second;30/minute;600/hour;12000/day")
@auth_required
def pull_slots(v):
	try:
		wager = int(request.values.get("wager"))
	except:
		return {"error": "Invalid wager."}

	try:
		currency = request.values.get("currency")
	except:
		return {"error": "Invalid currency (expected 'dramacoin' or 'marseybux')."}

	if (currency == "dramacoin" and wager > v.coins) or (currency == "marseybux" and wager > v.procoins):
		return {"error": f"Not enough {currency} to make that bet."}

	success, game_state = casino_slot_pull(v, wager, currency)

	if success:
		return {"game_state": game_state, "gambler": { "coins": v.coins, "procoins": v.procoins }}
	else:
		return {"error": "Wager must be more than 100 {currency}."}


@app.get("/casino/blackjack")
@limiter.limit("3/second;30/minute;600/hour;12000/day")
@auth_required
def get_player_blackjack_status(v):
	game, game_state = get_active_game(v)

	if game and game.active:
		safe_state = get_safe_game_state(v)
		return {"active": True, "game_state": safe_state}
	else:
		return {"active": False, "game_state": game_state}


@app.post("/casino/blackjack")
@limiter.limit("3/second;30/minute;600/hour;12000/day")
@auth_required
def deal_blackjack(v):
	try:
		wager = int(request.values.get("wager"))
	except:
		return {"error": "Invalid wager."}

	try:
		currency = request.values.get("currency")
	except:
		return {"error": "Invalid currency (expected 'dramacoin' or 'marseybux')."}

	if (currency == "dramacoin" and wager > v.coins) or (currency == "marseybux" and wager > v.procoins):
		return {"error": f"Not enough {currency} to make that bet."}

	success = deal_blackjack_game(v, wager, currency)

	if success:
		game, game_state = get_active_game(v)

		if game and game.active:
			safe_state = get_safe_game_state(v)
			return {"game_state": safe_state, "gambler": { "coins": v.coins, "procoins": v.procoins }}
		else:
			return {"game_state": game_state, "gambler": { "coins": v.coins, "procoins": v.procoins }}

	else:
		return {"error": "Wager must be more than 100 {currency}."}


@app.post("/casino/blackjack/action")
@limiter.limit("3/second;30/minute;600/hour;12000/day")
@auth_required
def player_took_blackjack_action(v):
	try:
		action = request.values.get("action")
	except:
		return {"error": "Invalid action."}

	was_successful = False
	state = None

	if action == 'hit':
		success, game_state = gambler_hit(v)
		was_successful = success
		state = game_state
	elif action == 'stay':
		success, game_state = gambler_stayed(v)
		was_successful = success
		state = game_state
	elif action == 'double_down':
		success, game_state = gambler_doubled_down(v)
		was_successful = success
		state = game_state
	elif action == 'insure':
		success, game_state = gambler_purchased_insurance(v)
		was_successful = success
		state = game_state

	if was_successful:
		return {"active": True, "game_state": state, "gambler": { "coins": v.coins, "procoins": v.procoins }}
	else:
		return {"active": False, "game_state": None}
