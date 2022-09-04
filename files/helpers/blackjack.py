import json
from json.encoder import INFINITY
import random
from math import floor
from files.helpers.const import *
from files.classes.casino_game import Casino_Game
from flask import g

deck_count = 4
ranks = ("2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A")
suits = ("S", "H", "C", "D")
minimum_bet = 100
maximum_bet = INFINITY


def build_game(gambler, currency_kind, wager):
    casino_game = Casino_Game()
    casino_game.user_id = gambler.id
    casino_game.currency = currency_kind
    casino_game.wager = wager
    casino_game.winnings = 0
    casino_game.kind = 'blackjack'
    casino_game.game_state = json.dumps(build_initial_state())
    g.db.add(casino_game)
    g.db.flush()


def build_initial_state():
    player, dealer, deck = deal_initial_cards()
    state = {
        "player": player,
        "dealer": dealer,
        "deck": deck,
        "actions": [],
        "insurance": False,
        "doubled_down": False,
        "status": "active"
    }

    state['actions'] = determine_actions(state)

    return state


def save_game_state(game, new_state):
    game.game_state = json.dumps(new_state)
    g.db.add(game)


def get_active_game(gambler):
    game = g.db.query(Casino_Game) \
        .filter(Casino_Game.active == True and
                Casino_Game.kind == 'blackjack' and
                Casino_Game.user_id == gambler.id).first()

    if game:
        return game, json.loads(game.game_state)
    else:
        return None, None


def get_safe_game_state(gambler):
    game, game_state = get_active_game(gambler)

    if game:
        return {
            "player": game_state['player'],
            "dealer": [game_state['dealer'][0], "?"],
            "actions": game_state['actions'],
            "insurance": game_state['insurance'],
            "doubled_down": game_state['doubled_down'],
            "status": game_state['status']
        }
    else:
        return None


def apply_blackjack_result(gambler):
    game, game_state = get_active_game(gambler)

    if game and game.active:
        result = game_state['status']

        if result == 'push' or result == 'insured_loss':
            reward = 0
        elif result == 'won':
            reward = game.wager
        elif result == 'blackjack':
            reward = floor(game.wager * 3/2)
        else:
            reward = -game.wager

        gambler.winnings += reward

        if (reward > -1):
            currency_value = int(getattr(gambler, game.currency, 0))
            setattr(gambler, game.currency,
                    currency_value + game.wager + reward)

        game.active = False
        game.winnings = reward
        g.db.add(game)


def deal_blackjack_game(gambler, wager_value, currency):
    over_min = wager_value >= minimum_bet
    under_max = wager_value <= maximum_bet
    using_dramacoin = currency == "dramacoin"
    using_marseybux = not using_dramacoin
    has_proper_funds = (using_dramacoin and gambler.coins >= wager_value) or (
        using_marseybux and gambler.procoins >= wager_value)
    currency_prop = "coins" if using_dramacoin else "procoins"
    currency_value = getattr(gambler, currency_prop, 0)

    if (over_min and under_max and has_proper_funds):
        # Charge the gambler for the game, reduce their winnings, and start the game.
        setattr(gambler, currency_prop, currency_value - wager_value)
        gambler.winnings -= wager_value

        build_game(gambler, currency_prop, wager_value)

        game, game_state = get_active_game(gambler)
        player_value = get_hand_value(game_state['player'])
        dealer_value = get_hand_value(game_state['dealer'])

        if player_value == 21 and dealer_value == 21:
            game_state["status"] = 'push'
            save_game_state(game, game_state)
            apply_blackjack_result(gambler)
        elif player_value == 21:
            game_state["status"] = 'blackjack'
            save_game_state(game, game_state)
            apply_blackjack_result(gambler)

        g.db.flush()

        return True
    else:
        return False

# region Actions


def gambler_hit(gambler):
    game, game_state = get_active_game(gambler.id)

    if game:
        player = game_state['player']
        deck = game_state['deck']
        doubled_down = game_state['doubled_down']
        player.append(deck.pop(0))
        player_value = get_hand_value(player)
        went_bust = player_value == -1
        five_card_charlied = len(player) >= 5

        if went_bust:
            game_state['status'] = 'bust'
            save_game_state(game, game_state)
            apply_blackjack_result(gambler)
        elif five_card_charlied:
            game_state['status'] = 'won'
            save_game_state(game, game_state)
            apply_blackjack_result(gambler)
        else:
            save_game_state(game, game_state)

        if doubled_down or player_value == 21:
            forced_stay_success, forced_stay_state = gambler_stayed(gambler)
            return forced_stay_success, forced_stay_state
        else:
            return True, game_state
    else:
        return False, game_state


def gambler_stayed(gambler):
    game, game_state = get_active_game(gambler.id)

    if game:
        player = game_state['player']
        dealer = game_state['dealer']
        deck = game_state['deck']
        insured = game_state['insurance']

        player_value = get_hand_value(player)
        dealer_value = get_hand_value(dealer)

        if dealer_value == 21 and insured:
            game_state["status"] = 'insured_loss'
            save_game_state(game, game_state)
            apply_blackjack_result(gambler)
        else:
            while dealer_value < 17 and dealer_value != -1:
                next = deck.pop(0)
                dealer.append(next)
                dealer_value = get_hand_value(dealer)

        if player_value > dealer_value or dealer_value == -1:
            game_state["status"] = 'won'
        elif dealer_value > player_value:
            game_state["status"] = 'lost'
        else:
            game_state["status"] = 'push'

        save_game_state(game, game_state)
        apply_blackjack_result(gambler)

        return True, game_state
    else:
        return False, game_state


def gambler_doubled_down(gambler):
    game, game_state = get_active_game(gambler.id)

    if game and not game_state['doubled_down']:
        currency_value = getattr(gambler, game.currency, 0)

        if (currency_value < game.wager):
            return False

        setattr(gambler, game.currency, currency_value - game.wager)
        game.wager *= 2
        game_state['doubled_down'] = True
        save_game_state(game, game_state)

        g.db.flush()

        last_hit_success, last_hit_state = gambler_hit(gambler)

        return last_hit_success, last_hit_state
    else:
        return False, game_state


def gambler_purchased_insurance(gambler):
    game, game_state = get_active_game(gambler.id)

    if game and not game_state['insurance']:
        insurance_cost = game.wager / 2
        currency_value = getattr(gambler, game.currency, 0)

        if (currency_value < insurance_cost):
            return False, game_state

        setattr(gambler, game.currency, currency_value - insurance_cost)
        game_state['insurance'] = True
        game_state['actions'] = determine_actions(game_state)
        save_game_state(game, game_state)

        return True, game_state
    else:
        return False, game_state

# endregion

# region Utilities


def shuffle(x):
    random.shuffle(x)
    return x


def determine_actions(state):
    actions = ['hit', 'stay', 'double_down']

    if (state['dealer'][0][0] == "A" and not state['insurance']):
        actions.append('insure')

    return actions


def deal_initial_cards():
    deck = shuffle(
        [rank + suit for rank in ranks for suit in suits for _ in range(deck_count)])
    p1, d1, p2, d2, *rest_of_deck = deck
    return [p1, p2], [d1, d2], rest_of_deck


def get_card_value(card):
    rank = card[0]
    return 0 if rank == "A" else min(ranks.index(rank) + 2, 10)


def get_hand_value(hand):
    without_aces = sum(map(get_card_value, hand))
    ace_count = sum("A" in c for c in hand)
    possibilities = []

    for i in range(ace_count + 1):
        value = without_aces + (ace_count - i) + i * 11
        possibilities.append(-1 if value > 21 else value)

    return max(possibilities)

# endregion
