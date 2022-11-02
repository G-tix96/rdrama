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
	chart(kind='daily', site=site)
	chart(kind='weekly', site=site)

def chart(kind, site):
	now = time.gmtime()
	midnight_this_morning = time.struct_time((
		now.tm_year, now.tm_mon, now.tm_mday,
		0, 0, 0,
		now.tm_wday, now.tm_yday, 0))
	today_cutoff = calendar.timegm(midnight_this_morning)

	if SITE == 'rdrama.net':
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

	signup_chart = plt.subplot2grid((chart_width, 20), (0, 0), rowspan=6, colspan=chart_width)
	posts_chart = plt.subplot2grid((chart_width, 20), (10, 0), rowspan=6, colspan=chart_width)
	comments_chart = plt.subplot2grid((chart_width, 20), (20, 0), rowspan=6, colspan=chart_width)

	signup_chart.grid(), posts_chart.grid(), comments_chart.grid()

	signup_chart.plot(daily_times, daily_signups, color='red')
	posts_chart.plot(daily_times, post_stats, color='blue')
	comments_chart.plot(daily_times, comment_stats, color='purple')

	signup_chart.set_ylim(ymin=0)
	posts_chart.set_ylim(ymin=0)
	comments_chart.set_ylim(ymin=0)

	signup_chart.set_ylabel("Signups")
	posts_chart.set_ylabel("Posts")
	comments_chart.set_ylabel("Comments")
	comments_chart.set_xlabel("Time (UTC)")

	file = chart_path(kind, site)

	plt.savefig(file, bbox_inches='tight')
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

	t = time.time()
	one = g.db.query(Marsey).filter(Marsey.submitter_id==None).count()
	print(f'one: {time.time() - t}', flush=True)

	t = time.time()
	two = g.db.query(User).count()
	print(f'two: {time.time() - t}', flush=True)

	t = time.time()
	three = g.db.query(User).filter_by(is_private=True).count()
	print(f'three: {time.time() - t}', flush=True)

	t = time.time()
	four = g.db.query(User).filter(User.is_banned > 0).count()
	print(f'four: {time.time() - t}', flush=True)

	t = time.time()
	five = g.db.query(User).filter_by(is_activated=True).count()
	print(f'five: {time.time() - t}', flush=True)

	t = time.time()
	six = g.db.query(func.sum(User.coins)).scalar()
	print(f'six: {time.time() - t}', flush=True)

	t = time.time()
	seven = g.db.query(func.sum(User.coins_spent)).scalar()
	print(f'seven: {time.time() - t}', flush=True)

	t = time.time()
	eight = g.db.query(User).filter(User.created_utc > day).count()
	print(f'eight: {time.time() - t}', flush=True)

	t = time.time()
	nine = g.db.query(Submission).count()
	print(f'nine: {time.time() - t}', flush=True)

	t = time.time()
	ten = g.db.query(Submission.author_id).distinct().count()
	print(f'ten: {time.time() - t}', flush=True)

	t = time.time()
	eleven = g.db.query(Submission).filter_by(is_banned=False).filter(Submission.deleted_utc == 0).count()
	print(f'eleven: {time.time() - t}', flush=True)

	t = time.time()
	twelve = g.db.query(Submission).filter_by(is_banned=True).count()
	print(f'twelve: {time.time() - t}', flush=True)

	t = time.time()
	thirteen = g.db.query(Submission).filter(Submission.deleted_utc > 0).count()
	print(f'thirteen: {time.time() - t}', flush=True)

	t = time.time()
	fourteen = g.db.query(Submission).filter(Submission.created_utc > day).count()
	print(f'fourteen: {time.time() - t}', flush=True)

	t = time.time()
	fifteen = g.db.query(Comment).filter(Comment.author_id != AUTOJANNY_ID).count()
	print(f'fifteen: {time.time() - t}', flush=True)

	t = time.time()
	sixteen = g.db.query(Comment.author_id).distinct().count()
	print(f'sixteen: {time.time() - t}', flush=True)

	t = time.time()
	seventeen = g.db.query(Comment).filter_by(is_banned=True).count()
	print(f'seventeen: {time.time() - t}', flush=True)

	t = time.time()
	eighteen = g.db.query(Comment).filter(Comment.deleted_utc > 0).count()
	print(f'eighteen: {time.time() - t}', flush=True)

	t = time.time()
	ninteen = g.db.query(Comment).filter(Comment.created_utc > day, Comment.author_id != AUTOJANNY_ID).count()
	print(f'ninteen: {time.time() - t}', flush=True)

	t = time.time()
	twenty = g.db.query(Vote).count()
	print(f'twenty: {time.time() - t}', flush=True)

	t = time.time()
	twentyone = g.db.query(Vote.user_id).distinct().count()
	print(f'twentyone: {time.time() - t}', flush=True)

	t = time.time()
	twentytwo = g.db.query(CommentVote).count()
	print(f'twentytwo: {time.time() - t}', flush=True)

	t = time.time()
	twentythree = g.db.query(CommentVote.user_id).distinct().count()
	print(f'twentythree: {time.time() - t}', flush=True)

	t = time.time()
	twentyfour = g.db.query(Vote).filter_by(vote_type=1).count() + g.db.query(CommentVote.comment_id).filter_by(vote_type=1).count()
	print(f'twentyfour: {time.time() - t}', flush=True)

	t = time.time()
	twentyfive = g.db.query(Vote).filter_by(vote_type=-1).count() + g.db.query(CommentVote.comment_id).filter_by(vote_type=-1).count()
	print(f'twentyfive: {time.time() - t}', flush=True)

	t = time.time()
	twentysix = g.db.query(AwardRelationship).count()
	print(f'twentysix: {time.time() - t}', flush=True)

	t = time.time()
	twentyseven = g.db.query(AwardRelationship).filter(or_(AwardRelationship.submission_id != None, AwardRelationship.comment_id != None)).count()
	print(f'twentyseven: {time.time() - t}', flush=True)

	t = time.time()
	twentyeight = len(active_users)
	print(f'twentyeight: {time.time() - t}', flush=True)

	t = time.time()
	twentynine = g.db.query(User).filter(User.last_active > week).count()
	print(f'twentynine: {time.time() - t}', flush=True)

	t = time.time()
	thirty = g.db.query(User).filter(User.house.like('Furry%')).count()
	print(f'thirty: {time.time() - t}', flush=True)

	t = time.time()
	thirtyone = g.db.query(User).filter(User.house.like('Femboy%')).count()
	print(f'thirtyone: {time.time() - t}', flush=True)

	t = time.time()
	thirtytwo = g.db.query(User).filter(User.house.like('Vampire%')).count()
	print(f'thirtytwo: {time.time() - t}', flush=True)

	t = time.time()
	thirtythree = g.db.query(User).filter(User.house.like('Racist%')).count()
	print(f'thirtythree: {time.time() - t}', flush=True)

	t = time.time()
	thirtyfour = g.db.query(func.sum(User.truecoins)).filter(User.house.like('Furry%')).scalar(),
	print(f'thirtyfour: {time.time() - t}', flush=True)

	t = time.time()
	thirtyfive = g.db.query(func.sum(User.truecoins)).filter(User.house.like('Femboy%')).scalar()
	print(f'thirtyfive: {time.time() - t}', flush=True)

	t = time.time()
	thirtysix = g.db.query(func.sum(User.truecoins)).filter(User.house.like('Vampire%')).scalar()
	print(f'thirtysix: {time.time() - t}', flush=True)

	t = time.time()
	thirtyseven = g.db.query(func.sum(User.truecoins)).filter(User.house.like('Racist%')).scalar()
	print(f'thirtyseven: {time.time() - t}', flush=True)

	stats = {
			"marseys": one,
			"users": two,
			"private users": three,
			"banned users": four,
			"verified email users": five,
			"coins in circulation": six,
			"total shop sales": seven,
			"signups last 24h": eight,
			"total posts": nine,
			"posting users": ten,
			"listed posts": eleven,
			"removed posts (by admins)": twelve,
			"deleted posts (by author)": thirteen,
			"posts last 24h": fourteen,
			"total comments": fifteen,
			"commenting users": sixteen,
			"removed comments (by admins)": seventeen,
			"deleted comments (by author)": eighteen,
			"comments last_24h": ninteen,
			"post votes": twenty,
			"post voting users": twentyone,
			"comment votes": twentytwo,
			"comment voting users": twentythree,
			"total upvotes": twentyfour,
			"total downvotes": twentyfive,
			"total awards": twentysix,
			"awards given": twentyseven,
			"users who posted, commented, or voted in the past 7 days": twentyeight,
			"users online in the past 7 days": twentynine,
			}

	if SITE_NAME == 'rDrama' or FEATURES['HOUSES']:
		stats2 = {
			"House furry members": thirty,
			"House femboy members": thirtyone,
			"House vampire members": thirtytwo,
			"House racist members": thirtythree,
			"House furry total truescore": thirtyfour,
			"House femboy total truescore": thirtyfive,
			"House vampire total truescore": thirtysix,
			"House racist total truescore": thirtyseven,
			}
		stats.update(stats2)

	return stats
