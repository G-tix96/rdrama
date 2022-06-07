from flask import g
import time
import calendar
import matplotlib.pyplot as plt

from files.classes.user import User
from files.classes.submission import Submission
from files.classes.comment import Comment
from files.helpers.const import *

def generate_charts_task(site):
	chart(kind='daily',  site=site)
	chart(kind='weekly', site=site)

def chart(kind, site):
	now = time.gmtime()
	midnight_this_morning = time.struct_time((
		now.tm_year, now.tm_mon, now.tm_mday,
		0, 0, 0,
		now.tm_wday, now.tm_yday, 0))
	today_cutoff = calendar.timegm(midnight_this_morning)

	if site == 'rdrama.net':
		time_diff = time.time() - 1619827200
		num_of_weeks = int(time_diff / 604800)
		chart_width = int(num_of_weeks/1.4)
	else:
		num_of_weeks = 30
		chart_width = 30

	if kind == 'daily':
		day_cutoffs = [today_cutoff - 86400 * i for i in range(num_of_weeks)][1:]
	else:
		day_cutoffs = [today_cutoff - 86400 * 7 * i for i in range(num_of_weeks)][1:]
	day_cutoffs.insert(0, calendar.timegm(now))

	daily_times = [time.strftime('%d/%m', time.gmtime(day_cutoffs[i + 1])) 
		for i in range(len(day_cutoffs) - 1)][::-1]

	daily_signups = [g.db.query(User).filter(
			User.created_utc < day_cutoffs[i], 
			User.created_utc > day_cutoffs[i + 1]).count() 
		for i in range(len(day_cutoffs) - 1)][::-1]

	post_stats = [g.db.query(Submission).filter(
			Submission.created_utc < day_cutoffs[i], 
			Submission.created_utc > day_cutoffs[i + 1], 
			Submission.is_banned == False).count() 
		for i in range(len(day_cutoffs) - 1)][::-1]

	comment_stats = [g.db.query(Comment).filter(
			Comment.created_utc < day_cutoffs[i], 
			Comment.created_utc > day_cutoffs[i + 1],
			Comment.is_banned == False, 
			Comment.author_id.notin_((AUTOJANNY_ID,NOTIFICATIONS_ID))).count() 
		for i in range(len(day_cutoffs) - 1)][::-1]

	plt.rcParams['figure.figsize'] = (chart_width, 20)

	signup_chart   = plt.subplot2grid((chart_width, 20), ( 0, 0), rowspan=6, colspan=chart_width)
	posts_chart    = plt.subplot2grid((chart_width, 20), (10, 0), rowspan=6, colspan=chart_width)
	comments_chart = plt.subplot2grid((chart_width, 20), (20, 0), rowspan=6, colspan=chart_width)

	signup_chart.grid(), posts_chart.grid(), comments_chart.grid()

	signup_chart.plot  (daily_times, daily_signups, color='red')
	posts_chart.plot   (daily_times,    post_stats, color='blue')
	comments_chart.plot(daily_times, comment_stats,	color='purple')

	signup_chart.set_ylim(ymin=0)
	posts_chart.set_ylim(ymin=0)
	comments_chart.set_ylim(ymin=0)

	signup_chart.set_ylabel("Signups")
	posts_chart.set_ylabel("Posts")
	comments_chart.set_ylabel("Comments")
	comments_chart.set_xlabel("Time (UTC)")

	file = chart_path(kind, site)

	plt.savefig(file)
	plt.clf()
	return file

def chart_path(kind, site):
	return f'/{site}_{kind}.png'
