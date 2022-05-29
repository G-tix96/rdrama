from files.__main__ import app, limiter
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *


@app.post("/lottery/start")
@auth_required
def lottery_start(v):
    # Save changes
    g.db.commit()

    return {"message": "Lottershe started."}


@app.post("/lottery/end")
@auth_required
def lottery_end(v):
    # Save changes
    g.db.commit()

    return {"message": "Lottershe ended."}


@app.post("/lottery/buy")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def lottery_buy(v):
    if v.coins < 12:
        return {"error": "Lottershe tickets cost 12 dramacoins each."}, 400

    # Charge user for ticket
    v.coins -= 12

    # Check for active lottery
    pass

    # Save changes
    g.db.commit()

    return {"message": "Lottershe ticket purchased!", "stats": {"sessionEnds": 0, "prize": 0, "ticketsSoldSession": 0, "ticketsSoldTotal": 0, "ticketsHeldSession": 0, "ticketsHeldTotal": 0, "totalWinnings": 0}}


@app.get("/lottery/stats")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def lottery_stats(v):
    return {"message": {"sessionEnds": 0, "prize": 0, "ticketsSoldSession": 0, "ticketsSoldTotal": 0}}
