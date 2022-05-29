from files.__main__ import app, limiter
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.lottery import *


@app.post("/lottery/end")
@auth_required
def lottery_end(v):
    end_lottery_session(g)
    return {"message": "Lottery ended."}


@app.post("/lottery/start")
@auth_required
def lottery_start(v):
    start_new_lottery_session(g)
    return {"message": "Lottery started."}


@app.post("/lottery/buy")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def lottery_buy(v):
    success, message, lottery_stats = purchase_lottery_ticket(g, v)

    if success:
        return {"message": message, "stats": {"user": v.lottery_stats, "lottery": lottery_stats}}
    else:
        return {"error": message, "stats": {"user": v.lottery_stats, "lottery": lottery_stats}}


@app.get("/lottery/active")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def lottery_active(v):
    most_recent_lottery = get_most_recent_lottery(g)

    if most_recent_lottery is None or not most_recent_lottery.is_active:
        return {"message": "There is no active lottery."}

    return {"message": most_recent_lottery.stats}
