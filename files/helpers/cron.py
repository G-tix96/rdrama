from files.cli import g, app, db_session
import click
import files.helpers.const as const

import files.helpers.lottery as lottery
import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.helpers.awards as awards
import files.routes.static as route_static
from files.routes.subs import sub_inactive_purge_task

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1h', is_flag=True, help='Call every 1 hour.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
def cron(every_5m, every_1h, every_1d):
	g.db = db_session()

	if every_5m:
		lottery.check_if_end_lottery_task()
		offsitementions.offsite_mentions_task()

	if every_1h:
		pass

	if every_1d:
		stats.generate_charts_task(const.SITE)
		route_static.stats_cached()
		awards.award_timers_bots_task()
		sub_inactive_purge_task()


