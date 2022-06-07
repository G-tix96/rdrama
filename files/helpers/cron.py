from files.cli import g, app, db_session
import click
import files.helpers.lottery as lottery

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1h', is_flag=True, help='Call every 1 hour.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
def cron(every_5m, every_1h, every_1d):
	g.db = db_session()

	if every_5m:
		lottery.check_if_end_lottery_task()
	if every_1h:
		pass
	if every_1d:
		pass

