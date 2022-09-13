from files.__main__ import app, limiter, db_session
from files.helpers.wrappers import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.const import *
from files.helpers.wrappers import *


def get_game_feed(game):
    games = g.db.query(Casino_Game) \
        .filter(Casino_Game.active == False, Casino_Game.kind == game) \
        .order_by(Casino_Game.created_utc.desc()).limit(30).all()

    def format_game(game):
        user = g.db.query(User).filter(User.id == game.user_id).one()
        wonlost = 'lost' if game.winnings < 0 else 'won'
        relevant_currency = "dramacoin" if game.currency == "coins" else "marseybux"

        return {
            "user": user.username,
            "won_or_lost": wonlost,
            "amount": abs(game.winnings),
            "currency": relevant_currency
        }

    return list(map(format_game, games))


def get_game_leaderboard(game):
    timestamp_24h_ago = time.time() - 86400
    timestamp_all_time = 1662825600 # "All Time" starts on release day

    biggest_win_all_time = g.db.query(Casino_Game.user_id,	User.username, Casino_Game.currency, Casino_Game.winnings).select_from(
        Casino_Game).join(User).order_by(Casino_Game.winnings.desc()).filter(Casino_Game.kind == game, Casino_Game.created_utc > timestamp_all_time).limit(1).one_or_none()

    biggest_win_last_24h = g.db.query(Casino_Game.user_id,	User.username, Casino_Game.currency, Casino_Game.winnings).select_from(
        Casino_Game).join(User).order_by(Casino_Game.winnings.desc()).filter(Casino_Game.kind == game, Casino_Game.created_utc > timestamp_24h_ago).limit(1).one_or_none()

    biggest_loss_all_time = g.db.query(Casino_Game.user_id,	User.username, Casino_Game.currency, Casino_Game.winnings).select_from(
        Casino_Game).join(User).order_by(Casino_Game.winnings.asc()).filter(Casino_Game.kind == game, Casino_Game.created_utc > timestamp_all_time).limit(1).one_or_none()

    biggest_loss_last_24h = g.db.query(Casino_Game.user_id,	User.username, Casino_Game.currency, Casino_Game.winnings).select_from(
        Casino_Game).join(User).order_by(Casino_Game.winnings.asc()).filter(Casino_Game.kind == game, Casino_Game.created_utc > timestamp_24h_ago).limit(1).one_or_none()

    if not biggest_win_all_time:
        biggest_win_all_time = [None, None, None, 0]

    if not biggest_win_last_24h:
        biggest_win_last_24h = [None, None, None, 0]

    if not biggest_loss_all_time:
        biggest_loss_all_time = [None, None, None, 0]

    if not biggest_loss_last_24h:
        biggest_loss_last_24h = [None, None, None, 0]


    return {
        "all_time": {
            "biggest_win": {
				"user": biggest_win_all_time[1],
				"currency": biggest_win_all_time[2],
				"amount": biggest_win_all_time[3]
			},
            "biggest_loss": {
				"user": biggest_loss_all_time[1],
				"currency": biggest_loss_all_time[2],
				"amount": abs(biggest_loss_all_time[3])
			}
        },
        "last_24h": {
            "biggest_win": {
				"user": biggest_win_last_24h[1],
				"currency": biggest_win_last_24h[2],
				"amount": biggest_win_last_24h[3]
			},
            "biggest_loss": {
				"user": biggest_loss_last_24h[1],
				"currency": biggest_loss_last_24h[2],
				"amount": abs(biggest_loss_last_24h[3])
			}
        }
    }
