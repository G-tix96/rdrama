from flask import g, jsonify, render_template
from files.helpers.get import get_accounts_dict

from files.routes.wrappers import auth_required
from files.__main__ import app

@app.get('/events/worldcup2022/leaderboard')
@auth_required
def get_leaderboard(v):
	result = g.db.execute('''WITH bet_votes AS (
    SELECT opt.id AS option_id, opt.exclusive, sov.user_id
    FROM submission_option_votes sov
    LEFT OUTER JOIN (
        SELECT so.id, so.exclusive
        FROM submission_options so
        JOIN submissions p ON so.submission_id = p.id
        WHERE p.author_id = 30 AND p.created_utc > 1668953400 AND so.exclusive IN (2, 3)
    ) AS opt ON opt.id = sov.option_id
    WHERE opt.id IS NOT NULL
)
SELECT
    COALESCE(bet_won.user_id, bet_lost.user_id) AS user_id,
    (COALESCE(bet_won.count_won, 0) + COALESCE(bet_lost.count_lost, 0)) AS bets_total,
    COALESCE(bet_won.count_won, 0) AS bets_won
FROM (
    SELECT user_id, COUNT(*) AS count_won FROM bet_votes
    WHERE exclusive = 3 GROUP BY user_id) AS bet_won
FULL OUTER JOIN (
    SELECT user_id, COUNT(*) AS count_lost FROM bet_votes
    WHERE exclusive = 2 GROUP BY user_id) AS bet_lost
ON bet_won.user_id = bet_lost.user_id
ORDER BY bets_won DESC, bets_total ASC;''').all()
	if g.is_api_or_xhr: return jsonify(result)
	users = get_accounts_dict([r[0] for r in result], v=v, include_shadowbanned=False)
	return render_template("event/worldcup22_leaderboard.html", v=v, result=result, users=users)
