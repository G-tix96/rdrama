import time
from sqlalchemy import *
from files.helpers.wrappers import *

LOTTERY_TICKET_COST = 12

# The amount of dramacoins permanently removed from the economy to reduce expected value
SINK_RATE = 3

# The amount of dramacoins the lottery founders receive
ROYALTY_RATE = 1  

# The account in which royalties are to be deposited
ROYALTY_ACCOUNT_ID = 9  

# The account in which the prize is held to be accessed by anyone
MANAGER_ACCOUNT_ID = 3


def get_most_recent_lottery(g):
    lotteries = g.db.query(Lottery).order_by(Lottery.id.desc())
    count = 0
    mostRecent = None

    for lottery in lotteries:
        if count == 0:
            mostRecent = lottery
        count += 1

    return mostRecent


def end_lottery_session(g):
    # Check that a current session exists
    most_recent_lottery = get_most_recent_lottery(g)

    if (most_recent_lottery is None or not most_recent_lottery.is_active):
        return

    # Calculate players and odds
    

    # Payout to winner

    # Send DM to all involved

    most_recent_lottery.is_active = False

    # Save changes
    g.db.commit()


def start_new_lottery_session(g):
    # Wrap up current session
    end_lottery_session(g)

    # Create new session
    lottery = Lottery()
    epoch_time = int(time.time())
    one_week_from_now = epoch_time + 60 * 60 * 24 * 7
    lottery.ends_at = one_week_from_now
    lottery.is_active = True

    # Save changes
    g.db.add(lottery)
    g.db.commit()


def purchase_lottery_ticket(g, v):
    if (v.coins < LOTTERY_TICKET_COST):
        return False, f'Lottery tickets cost {LOTTERY_TICKET_COST} dramacoins each.', None

    most_recent_lottery = get_most_recent_lottery(g)
    if (most_recent_lottery is None or not most_recent_lottery.is_active):
        return False, "There is no active lottery.", None

    # Charge the user and update the lottery
    v.coins -= LOTTERY_TICKET_COST
    v.currently_held_lottery_tickets += 1
    v.total_held_lottery_tickets += 1

    net_ticket_value = LOTTERY_TICKET_COST - SINK_RATE - ROYALTY_RATE
    most_recent_lottery.prize += net_ticket_value
    most_recent_lottery.tickets_sold += 1

    # Pass the holdings to the lottery manager
    manager = g.db.query(User).get(MANAGER_ACCOUNT_ID)
    manager.coins += net_ticket_value

    # Pay royalties
    beneficiary = g.db.query(User).get(ROYALTY_ACCOUNT_ID)
    beneficiary.coins += ROYALTY_RATE

    # Save changes
    g.db.commit()

    return True, 'Successfully purchased a lottery ticket!', most_recent_lottery.stats
