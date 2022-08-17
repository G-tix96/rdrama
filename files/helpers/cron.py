from files.cli import g, app, db_session
import click
from files.helpers.const import *
from files.helpers.alerts import send_repeatable_notification
from files.classes import *

import files.helpers.lottery as lottery
import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.helpers.awards as awards
import files.routes.static as route_static

from sys import stdout
import datetime
import time
import requests

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1h', is_flag=True, help='Call every 1 hour.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
@click.option('--every-1mo', is_flag=True, help='Call every 1 month.')
def cron(every_5m, every_1h, every_1d, every_1mo):
	g.db = db_session()

	if every_5m:
		lottery.check_if_end_lottery_task()
		offsitementions.offsite_mentions_task()

	if every_1h:
		awards.award_timers_bots_task()

	if every_1d:
		stats.generate_charts_task(SITE)
		route_static.stats_cached()
		sub_inactive_purge_task()

	if every_1mo:
		give_monthly_marseybux_task()

	g.db.commit()
	g.db.close()
	stdout.flush()

def sub_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in g.db.query(Submission.sub).distinct() \
		.filter(Submission.sub != None, Submission.created_utc > one_week_ago).all()]
	active_holes.append('changelog') # system hole immune from deletion

	dead_holes = g.db.query(Sub).filter(Sub.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level > 1).all()]

	mods = g.db.query(Mod).filter(Mod.sub.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f":marseyrave: /h/{x.sub} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	for name in names:
		for admin in admins:
			send_repeatable_notification(admin, f":marseyrave: /h/{name} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	posts = g.db.query(Submission).filter(Submission.sub.in_(names)).all()
	for post in posts:
		post.sub = None
		g.db.add(post)

	to_delete = mods \
		+ g.db.query(Exile).filter(Exile.sub.in_(names)).all() \
		+ g.db.query(SubBlock).filter(SubBlock.sub.in_(names)).all() \
		+ g.db.query(SubSubscription).filter(SubSubscription.sub.in_(names)).all()

	for x in to_delete:
		g.db.delete(x)

	for x in dead_holes:
		g.db.delete(x)

	return True


def give_monthly_marseybux_task():
	month = datetime.datetime.now() + datetime.timedelta(days=5)
	month = month.strftime('%B')

	data = {'access_token': GUMROAD_TOKEN}

	emails = [x['email'] for x in requests.get(f'https://api.gumroad.com/v2/products/{GUMROAD_ID}/subscribers', data=data, timeout=5).json()["subscribers"]]

	for u in g.db.query(User).filter(User.patron > 0, User.patron_utc == 0).all():
		g.db.add(u)
		if u.admin_level or u.id == A_ID or (u.email and u.email.lower() in emails):
			procoins = procoins_li[u.patron]
			u.procoins += procoins
			send_repeatable_notification(u.id, f"@AutoJanny has given you {procoins} Marseybux for the month of {month}! You can use them to buy awards in the [shop](/shop).")
		else: u.patron = 0

	ma = ModAction(
		kind="monthly",
		user_id=SNAPPY_ID,
	)
	g.db.add(ma)

	return True

