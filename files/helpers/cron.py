from files.cli import g, app, db_session
import click
from files.helpers.const import *
from files.helpers.alerts import send_repeatable_notification
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.get import *
from files.helpers.actions import *
from files.classes import *
from files.__main__ import cache

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
		if FEATURES['GAMBLING']:
			lottery.check_if_end_lottery_task()
			spin_roulette_wheel()
		offsitementions.offsite_mentions_task()
		if SITE == 'pcmemes.net':
			route_static.live_cached()

	if every_1h:
		awards.award_timers_bots_task()

	if every_1d:
		stats.generate_charts_task(SITE)
		sub_inactive_purge_task()
		cache.delete_memoized(route_static.stats_cached)
		route_static.stats_cached()

	if every_1mo:
		if KOFI_LINK: give_monthly_marseybux_task_kofi()
		else: give_monthly_marseybux_task()

	g.db.commit()
	g.db.close()
	stdout.flush()

def sub_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in g.db.query(Submission.sub).distinct() \
		.filter(Submission.sub != None, Submission.created_utc > one_week_ago,
			Submission.private == False, Submission.is_banned == False,
			Submission.deleted_utc == 0).all()]
	active_holes.append('changelog') # system hole immune from deletion

	dead_holes = g.db.query(Sub).filter(Sub.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_INACTIVITY_DELETION']).all()]

	mods = g.db.query(Mod).filter(Mod.sub.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f":marseyrave: /h/{x.sub} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	for name in names:
		first_mod_id = g.db.query(Mod.user_id).filter_by(sub=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f'Brought a Hole into this world, only to let it die (/h/{name})'
			)

		for admin in admins:
			send_repeatable_notification(admin, f":marseyrave: /h/{name} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	posts = g.db.query(Submission).filter(Submission.sub.in_(names)).all()
	for post in posts:
		post.sub = None
		g.db.add(post)

	to_delete = mods \
		+ g.db.query(Exile).filter(Exile.sub.in_(names)).all() \
		+ g.db.query(SubBlock).filter(SubBlock.sub.in_(names)).all() \
		+ g.db.query(SubJoin).filter(SubJoin.sub.in_(names)).all() \
		+ g.db.query(SubSubscription).filter(SubSubscription.sub.in_(names)).all()

	for x in to_delete:
		g.db.delete(x)
	g.db.flush()

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
		if u.admin_level or u.id in GUMROAD_MESSY or (u.email and u.email.lower() in emails):
			procoins = procoins_li[u.patron]
			u.procoins += procoins
			send_repeatable_notification(u.id, f"@AutoJanny has given you {procoins} Marseybux for the month of {month}! You can use them to buy awards in the [shop](/shop).")
		else: u.patron = 0

	ma = ModAction(
		kind="monthly",
		user_id=AUTOJANNY_ID,
	)
	g.db.add(ma)

	return True


def give_monthly_marseybux_task_kofi():
	month = datetime.datetime.now() + datetime.timedelta(days=5)
	month = month.strftime('%B')

	tx_emails = [x[0] for x in g.db.query(Transaction.email).distinct().all()]

	for u in g.db.query(User).filter(User.patron > 0, User.patron_utc == 0).all():
		g.db.add(u)

		if not (u.is_activated and u.email in tx_emails):
			u.patron = 0
			continue

		procoins = procoins_li[u.patron]
		u.procoins += procoins
		send_repeatable_notification(u.id, f"@AutoJanny has given you {procoins} Marseybux for the month of {month}! You can use them to buy awards in the [shop](/shop).")

	ma = ModAction(
		kind="monthly",
		user_id=AUTOJANNY_ID,
	)
	g.db.add(ma)

	return True
