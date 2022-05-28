from files.__main__ import app, limiter
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *

@app.post("/lottery/buy")
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@auth_required
def lottery_buy(v):
    if v.coins < 12:
        return {"error": "Lottershe tickets cost 12 dramacoins each."}, 400

    # Charge user for ticket
    v.coins -= 12

    # Save changes
    g.db.commit()

    return {"message": "Lottershe ticket purchased!"}
