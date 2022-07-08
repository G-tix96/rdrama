from flask import g
import time
import calendar
import matplotlib.pyplot as plt
from sqlalchemy import *

from files.classes.user import User
from files.classes.submission import Submission
from files.classes.comment import Comment
from files.classes.votes import Vote, CommentVote
from files.classes.marsey import Marsey
from files.classes.award import AwardRelationship
from files.helpers.const import *

def generate_charts_task(site):
	chart(kind='daily',  site=site)
	chart(kind='weekly', site=site)
	stats(site=site)

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
			Comment.author_id != AUTOJANNY_ID).count() 
		for i in range(len(day_cutoffs) - 1)][::-1]

	plt.rcParams['figure.figsize'] = (chart_width, 20)

	signup_chart   = plt.subplot2grid((chart_width, 20), ( 0, 0), rowspan=6, colspan=chart_width)
	posts_chart	= plt.subplot2grid((chart_width, 20), (10, 0), rowspan=6, colspan=chart_width)
	comments_chart = plt.subplot2grid((chart_width, 20), (20, 0), rowspan=6, colspan=chart_width)

	signup_chart.grid(), posts_chart.grid(), comments_chart.grid()

	signup_chart.plot  (daily_times, daily_signups, color='red')
	posts_chart.plot   (daily_times,	post_stats, color='blue')
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

def stats(site=None):
	day = int(time.time()) - 86400
	week = int(time.time()) - 604800
	posters = g.db.query(Submission.author_id).distinct(Submission.author_id).filter(Submission.created_utc > week).all()
	commenters = g.db.query(Comment.author_id).distinct(Comment.author_id).filter(Comment.created_utc > week).all()
	voters = g.db.query(Vote.user_id).distinct(Vote.user_id).filter(Vote.created_utc > week).all()
	commentvoters = g.db.query(CommentVote.user_id).distinct(CommentVote.user_id).filter(CommentVote.created_utc > week).all()
	active_users = set(posters) | set(commenters) | set(voters) | set(commentvoters)

	stats = {
			"marseys": g.db.query(Marsey).count(),
			"users": g.db.query(User).count(),
			"private users": g.db.query(User).filter_by(is_private=True).count(),
			"banned users": g.db.query(User).filter(User.is_banned > 0).count(),
			"verified email users": g.db.query(User).filter_by(is_activated=True).count(),
			"coins in circulation": g.db.query(func.sum(User.coins)).scalar(),
			"total shop sales": g.db.query(func.sum(User.coins_spent)).scalar(),
			"signups last 24h": g.db.query(User).filter(User.created_utc > day).count(),
			"total posts": g.db.query(Submission).count(),
			"posting users": g.db.query(Submission.author_id).distinct().count(),
			"listed posts": g.db.query(Submission).filter_by(is_banned=False).filter(Submission.deleted_utc == 0).count(),
			"removed posts (by admins)": g.db.query(Submission).filter_by(is_banned=True).count(),
			"deleted posts (by author)": g.db.query(Submission).filter(Submission.deleted_utc > 0).count(),
			"posts last 24h": g.db.query(Submission).filter(Submission.created_utc > day).count(),
			"total comments": g.db.query(Comment).filter(Comment.author_id != AUTOJANNY_ID).count(),
			"commenting users": g.db.query(Comment.author_id).distinct().count(),
			"removed comments (by admins)": g.db.query(Comment).filter_by(is_banned=True).count(),
			"deleted comments (by author)": g.db.query(Comment).filter(Comment.deleted_utc > 0).count(),
			"comments last_24h": g.db.query(Comment).filter(Comment.created_utc > day, Comment.author_id != AUTOJANNY_ID).count(),
			"post votes": g.db.query(Vote).count(),
			"post voting users": g.db.query(Vote.user_id).distinct().count(),
			"comment votes": g.db.query(CommentVote).count(),
			"comment voting users": g.db.query(CommentVote.user_id).distinct().count(),
			"total upvotes": g.db.query(Vote).filter_by(vote_type=1).count() + g.db.query(CommentVote.comment_id).filter_by(vote_type=1).count(),
			"total downvotes": g.db.query(Vote).filter_by(vote_type=-1).count() + g.db.query(CommentVote.comment_id).filter_by(vote_type=-1).count(),
			"total awards": g.db.query(AwardRelationship).count(),
			"awards given": g.db.query(AwardRelationship).filter(or_(AwardRelationship.submission_id != None, AwardRelationship.comment_id != None)).count(),
			"users who posted, commented, or voted in the past 7 days": len(active_users),
			"users online in the past 7 days": g.db.query(User).filter(User.last_active > week).count(),
			}

	if site == 'rDrama':
		stats2 = {
			"House furry members": g.db.query(User).filter(User.house.like('Furry%')).count(),
			"House femboy members": g.db.query(User).filter(User.house.like('Femboy%')).count(),
			"House vampire members": g.db.query(User).filter(User.house.like('Vampire%')).count(),
			"House racist members": g.db.query(User).filter(User.house.like('Racist%')).count(),
			"House furry total truescore": g.db.query(func.sum(User.truecoins)).filter(User.house.like('Furry%')).scalar(),
			"House femboy total truescore": g.db.query(func.sum(User.truecoins)).filter(User.house.like('Femboy%')).scalar(),
			"House vampire total truescore": g.db.query(func.sum(User.truecoins)).filter(User.house.like('Vampire%')).scalar(),
			"House racist total truescore": g.db.query(func.sum(User.truecoins)).filter(User.house.like('Racist%')).scalar(),
			}
		stats.update(stats2)

	return stats
