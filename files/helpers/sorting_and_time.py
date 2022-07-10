import time
from files.classes.comment import Comment
from files.classes.submission import Submission

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

def sort_comments(sort, comments):

	if sort == 'new':
		return comments.order_by(Comment.id.desc())
	elif sort == 'old':
		return comments.order_by(Comment.id)
	elif sort == 'controversial':
		return comments.order_by((Comment.upvotes+1)/(Comment.downvotes+1) + (Comment.downvotes+1)/(Comment.upvotes+1), Comment.downvotes.desc(), Comment.id.desc())
	elif sort == "bottom":
		return comments.order_by(Comment.upvotes - Comment.downvotes)
	elif SITE == 'watchpeopledie.co':
		return comments.order_by(Comment.downvotes - Comment.upvotes, Comment.id.desc())
	else:
		return comments.order_by(Comment.realupvotes.desc(), Comment.id.desc())

def sort_posts(sort, posts):
	if sort == "new":
		return posts.order_by(Submission.created_utc.desc())
	elif sort == "old":
		return posts.order_by(Submission.created_utc)
	elif sort == "controversial":
		return posts.order_by((Submission.upvotes+1)/(Submission.downvotes+1) + (Submission.downvotes+1)/(Submission.upvotes+1), Submission.downvotes.desc(), Submission.created_utc.desc())
	elif sort == "bottom":
		return posts.order_by(Submission.upvotes - Submission.downvotes, Submission.created_utc.desc())
	elif sort == "comments":
		return posts.order_by(Submission.comment_count.desc(), Submission.created_utc.desc())
	else:
		return posts.order_by(Submission.downvotes - Submission.upvotes, Submission.created_utc.desc())