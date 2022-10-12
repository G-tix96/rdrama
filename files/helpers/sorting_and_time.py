import time
from files.classes.comment import Comment
from files.classes.submission import Submission
from files.helpers.const import *
from sqlalchemy.sql import func

def apply_time_filter(t, objects, Class):
	now = int(time.time())
	if t == 'hour':
		cutoff = now - 3600
	elif t == 'day':
		cutoff = now - 86400
	elif t == 'week':
		cutoff = now - 604800
	elif t == 'month':
		cutoff = now - 2592000
	elif t == 'year':
		cutoff = now - 31536000
	else:
		cutoff = 0

	return objects.filter(Class.created_utc >= cutoff)

def sort_objects(sort, objects, Class):
	if sort == 'hot':
		ti = int(time.time()) + 3600
		if SITE_NAME == 'rDrama': metric = Class.realupvotes
		else: metric = Class.upvotes - Class.downvotes
		if Class == Submission: metric += Class.comment_count/5
		return objects.order_by(-1000000*(metric + 1)/(func.power(((ti - Class.created_utc)/1000), 1.23)), Class.created_utc.desc())
	elif sort == "bump" and Class == Submission:
		return objects.filter(Class.comment_count > 1).order_by(Class.bump_utc.desc(), Class.created_utc.desc())
	elif sort == "comments" and Class == Submission:
		return objects.order_by(Class.comment_count.desc(), Class.created_utc.desc())
	elif sort == "new":
		return objects.order_by(Class.created_utc.desc())
	elif sort == "old":
		return objects.order_by(Class.created_utc)
	elif sort == "controversial":
		return objects.order_by((Class.upvotes+1)/(Class.downvotes+1) + (Class.downvotes+1)/(Class.upvotes+1), Class.downvotes.desc(), Class.created_utc.desc())
	elif sort == "bottom":
		return objects.order_by(Class.upvotes - Class.downvotes, Class.created_utc.desc())
	else:
		return objects.order_by(Class.downvotes - Class.upvotes, Class.created_utc.desc())
