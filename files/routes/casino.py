from files.__main__ import app
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.wrappers import *
from files.helpers.casino import *
from files.helpers.slots import *
from files.helpers.twentyone import *
from files.helpers.roulette import *
from files.helpers.lottery import *


@app.get("/casino")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def casino(v):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)

    return render_template("casino.html", v=v)


@app.get("/casino/<game>")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def casino_game_page(v, game):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)
    elif game not in CASINO_GAME_KINDS:
        abort(404)

    feed = json.dumps(get_game_feed(game))
    leaderboard = json.dumps(get_game_leaderboard(game))

    game_state = ''
    if game == 'blackjack':
        if get_active_twentyone_game(v):
            game_state = json.dumps(get_active_twentyone_game_state(v))

    return render_template(
        f"casino/{game}_screen.html",
        v=v,
        game=game,
        feed=feed,
        leaderboard=leaderboard,
        game_state=game_state
    )


@app.get("/casino/<game>/feed")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def casino_game_feed(v, game):
    if v.rehab: 
        abort(403, "You are under Rehab award effect!")
    elif game not in CASINO_GAME_KINDS:
        abort(404)

    feed = get_game_feed(game)
    return {"feed": feed}


# Lottershe
@app.get("/lottershe")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def lottershe(v):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)

    participants = get_users_participating_in_lottery()
    return render_template("lottery.html", v=v, participants=participants)

# Slots
@app.post("/casino/slots")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def pull_slots(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        wager = int(request.values.get("wager"))
    except:
        abort(400, "Invalid wager.")

    try:
        currency = request.values.get("currency")
    except:
        abort(400, "Invalid currency (expected 'coin' or 'marseybux').")

    if (currency == "coin" and wager > v.coins) or (currency == "marseybux" and wager > v.procoins):
        abort(400, f"Not enough {currency} to make that bet")

    success, game_state = casino_slot_pull(v, wager, currency)

    if success:
        return {"game_state": game_state, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    else:
        abort(400, f"Wager must be more than 5 {currency}")


# 21
@app.post("/casino/twentyone/deal")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def blackjack_deal_to_player(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        wager = int(request.values.get("wager"))
        currency = request.values.get("currency")
        create_new_game(v, wager, currency)
        state = dispatch_action(v, BlackjackAction.DEAL)
        feed = get_game_feed('blackjack')

        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except Exception as e:
        abort(400, str(e))


@app.post("/casino/twentyone/hit")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def blackjack_player_hit(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        state = dispatch_action(v, BlackjackAction.HIT)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        abort(400, "Unable to hit.")


@app.post("/casino/twentyone/stay")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def blackjack_player_stay(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        state = dispatch_action(v, BlackjackAction.STAY)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        abort(400, "Unable to stay.")


@app.post("/casino/twentyone/double-down")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def blackjack_player_doubled_down(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        state = dispatch_action(v, BlackjackAction.DOUBLE_DOWN)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        abort(400, "Unable to double down.")


@app.post("/casino/twentyone/buy-insurance")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def blackjack_player_bought_insurance(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        state = dispatch_action(v, BlackjackAction.BUY_INSURANCE)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        abort(403, "Unable to buy insurance.")

# Roulette
@app.get("/casino/roulette/bets")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def roulette_get_bets(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    bets = get_roulette_bets()

    return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "procoins": v.procoins}}


@app.post("/casino/roulette/place-bet")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
@feature_required('GAMBLING')
def roulette_player_placed_bet(v):
    if v.rehab:
        abort(403, "You are under Rehab award effect!")

    try:
        bet = request.values.get("bet")
        which = request.values.get("which")
        amount = int(request.values.get("wager"))
        currency = request.values.get("currency")

        if amount < 5:
            abort(400, f"Minimum bet is 5 {currency}.")

        gambler_placed_roulette_bet(v, bet, which, amount, currency)

        bets = get_roulette_bets()

        return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        abort(400, "Unable to place a bet.")
