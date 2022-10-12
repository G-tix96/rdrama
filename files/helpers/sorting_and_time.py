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
