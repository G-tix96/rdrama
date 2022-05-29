import time
from random import choice
from sqlalchemy import *
from files.helpers.alerts import *
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


def get_active_lottery(g):
    return g.db.query(Lottery).order_by(Lottery.id.desc()).filter(Lottery.is_active).one_or_none()

def get_active_lottery_stats(g):
    active_lottery = get_active_lottery(g)
    return None if active_lottery is None else active_lottery.stats

def end_lottery_session(g):
    active_lottery = get_active_lottery(g)

    if (active_lottery is None):
        return False, "There is no active lottery."

    participating_users = g.db.query(User).filter(
        User.currently_held_lottery_tickets > 0).all()

    raffle = []
    for user in participating_users:
        for _ in range(user.currently_held_lottery_tickets):
            raffle.append(user.id)


    winner = choice(raffle)
    winning_user = next(filter(lambda x: x.id == winner, participating_users))
    winning_user.coins += active_lottery.prize
    winning_user.total_lottery_winnings += active_lottery.prize

    for user in participating_users:
        chance_to_win = user.currently_held_lottery_tickets / raffle.count
        notification_text = f'You won {active_lottery.prize} the lottery! Congratulations!\nOdds of winning: {chance_to_win}%' if user.id == winner else "You did not win the lottery. Better luck next time!\nOdds of winning: {chance_to_win}%"
        send_notification(user.id, notification_text)
        user.currently_held_lottery_tickets = 0


    active_lottery.is_active = False

    manager = g.db.query(User).get(MANAGER_ACCOUNT_ID)
    manager.coins -= active_lottery.prize

    g.db.commit()

    return True, f'{winning_user.username} won {active_lottery.prize} dramacoins!'


def start_new_lottery_session(g):
    end_lottery_session(g)

    lottery = Lottery()
    epoch_time = int(time.time())
    one_week_from_now = epoch_time + 60 * 60 * 24 * 7
    lottery.ends_at = one_week_from_now
    lottery.is_active = True

    g.db.add(lottery)
    g.db.commit()


def purchase_lottery_ticket(g, v):
    if (v.coins < LOTTERY_TICKET_COST):
        return False, f'Lottery tickets cost {LOTTERY_TICKET_COST} dramacoins each.', None

    most_recent_lottery = get_active_lottery(g)
    if (most_recent_lottery is None):
        return False, "There is no active lottery.", None

    v.coins -= LOTTERY_TICKET_COST
    v.currently_held_lottery_tickets += 1
    v.total_held_lottery_tickets += 1

    net_ticket_value = LOTTERY_TICKET_COST - SINK_RATE - ROYALTY_RATE
    most_recent_lottery.prize += net_ticket_value
    most_recent_lottery.tickets_sold += 1

    manager = g.db.query(User).get(MANAGER_ACCOUNT_ID)
    manager.coins += net_ticket_value

    beneficiary = g.db.query(User).get(ROYALTY_ACCOUNT_ID)
    beneficiary.coins += ROYALTY_RATE

    g.db.commit()

    return True, 'Successfully purchased a lottery ticket!', most_recent_lottery.stats
