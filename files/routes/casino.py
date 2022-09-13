from files.__main__ import app
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.wrappers import *
from files.helpers.slots import *
from files.helpers.lottery import *
from files.helpers.casino import *
from files.helpers.twentyone import *
from files.helpers.roulette import *


@app.get("/casino")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def casino(v):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)

    return render_template("casino.html", v=v)


@app.get("/casino/<game>")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def casino_game_page(v, game):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)

    feed = json.dumps(get_game_feed(game))
    leaderboard = json.dumps(get_game_leaderboard(game))

    return render_template(
        f"casino/{game}_screen.html",
        v=v,
        game=game,
        feed=feed,
        leaderboard=leaderboard
    )


@app.get("/casino/<game>/feed")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def casino_game_feed(v, game):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    feed = get_game_feed(game)
    return {"feed": feed}


# Lottershe
@app.get("/lottershe")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def lottershe(v):
    if v.rehab:
        return render_template("casino/rehab.html", v=v)

    participants = get_users_participating_in_lottery()
    return render_template("lottery.html", v=v, participants=participants)

# Slots
@app.post("/casino/slots")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def pull_slots(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        wager = int(request.values.get("wager"))
    except:
        return {"error": "Invalid wager."}, 400

    try:
        currency = request.values.get("currency")
    except:
        return {"error": "Invalid currency (expected 'dramacoin' or 'marseybux')."}, 400

    if (currency == "dramacoin" and wager > v.coins) or (currency == "marseybux" and wager > v.procoins):
        return {"error": f"Not enough {currency} to make that bet."}, 400

    success, game_state = casino_slot_pull(v, wager, currency)

    if success:
        return {"game_state": game_state, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    else:
        return {"error": f"Wager must be more than 5 {currency}."}, 400


# 21
@app.post("/casino/twentyone/deal")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def blackjack_deal_to_player(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        wager = int(request.values.get("wager"))
        currency = request.values.get("currency")
        create_new_game(v, wager, currency)
        state = dispatch_action(v, BlackjackAction.DEAL)
        feed = get_game_feed('blackjack')

        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except Exception as e:
        return {"error": str(e)}, 400


@app.post("/casino/twentyone/hit")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def blackjack_player_hit(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        state = dispatch_action(v, BlackjackAction.HIT)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        return {"error": "Unable to hit."}, 400


@app.post("/casino/twentyone/stay")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def blackjack_player_stay(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        state = dispatch_action(v, BlackjackAction.STAY)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        return {"error": "Unable to stay."}, 400


@app.post("/casino/twentyone/double-down")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def blackjack_player_doubled_down(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        state = dispatch_action(v, BlackjackAction.DOUBLE_DOWN)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        return {"error": "Unable to double down."}, 400


@app.post("/casino/twentyone/buy-insurance")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def blackjack_player_bought_insurance(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        state = dispatch_action(v, BlackjackAction.BUY_INSURANCE)
        feed = get_game_feed('blackjack')
        return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        return {"error": "Unable to buy insurance."}, 400

# Roulette
@app.get("/casino/roulette/bets")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def roulette_get_bets(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    bets = get_roulette_bets()

    return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "procoins": v.procoins}}


@app.post("/casino/roulette/place-bet")
@limiter.limit("100/minute;2000/hour;12000/day")
@auth_required
def roulette_player_placed_bet(v):
    if v.rehab:
        return {"error": "You are under Rehab award effect!"}, 400

    try:
        bet = request.values.get("bet")
        which = request.values.get("which")
        amount = int(request.values.get("wager"))
        currency = request.values.get("currency")

        if amount < 5:
            return {"error": f"Minimum bet is 5 {currency}."}

        gambler_placed_roulette_bet(v, bet, which, amount, currency)

        bets = get_roulette_bets()

        return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "procoins": v.procoins}}
    except:
        return {"error": "Unable to place a bet."}, 400