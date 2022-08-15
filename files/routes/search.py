from files.helpers.wrappers import *
import re
from sqlalchemy import *
from flask import *
from files.__main__ import app
from files.helpers.regex import *
from files.helpers.sorting_and_time import *

search_operator_hole = HOLE_NAME

valid_params = [
	'author',
	'domain',
	'over18',
	"post",
	"before",
	"after",
	search_operator_hole,
]

def searchparse(text):
	text = text.lower()

	criteria = {x[0]:x[1] for x in query_regex.findall(text)}
	for x in criteria:
		if x in valid_params:
			text = text.replace(f"{x}:{criteria[x]}", "")

	text = text.strip()
	if text:
		criteria['q'] = []
		for m in search_token_regex.finditer(text):
			token = m[1] if m[1] else m[2]
			# Escape SQL pattern matching special characters
			token = token.replace('\\', '').replace('_', '\_').replace('%', '\%')
			criteria['q'].append(token)

	return criteria

@app.get("/search/posts")
@auth_required
def searchposts(v):

	query = request.values.get("q", '').strip()

	page = max(1, int(request.values.get("page", 1)))

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria=searchparse(query)

	posts = g.db.query(Submission.id) \
				.join(Submission.author) \
				.filter(Submission.author_id.notin_(v.userblocks))
	
	if not v.paid_dues:
		posts = posts.filter(Submission.club == False)
	
	if v.admin_level < 2:
		posts = posts.filter(
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			Submission.private == False,
			User.shadowbanned == None)

	if 'author' in criteria:
		posts = posts.filter(Submission.ghost == False)
		author = get_user(criteria['author'])
		if not author: return {"error": "User not found"}
		if author.is_private and author.id != v.id and v.admin_level < 2 and not v.eye:
			if request.headers.get("Authorization"):
				return {"error": f"@{author.username}'s profile is private; You can't use the 'author' syntax on them"}
			return render_template("search.html",
								v=v,
								query=query,
								total=0,
								page=page,
								listing=[],
								sort=sort,
								t=t,
								next_exists=False,
								domain=None,
								domain_obj=None,
								error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them."
								)
		else: posts = posts.filter(Submission.author_id == author.id)

	if 'q' in criteria:
		words = [or_(Submission.title.ilike('%'+x+'%'), Submission.body.ilike('%'+x+'%')) \
					for x in criteria['q']]
		posts = posts.filter(*words)
		
	if 'over18' in criteria: posts = posts.filter(Submission.over_18==True)

	if 'domain' in criteria:
		domain=criteria['domain']

		domain = domain.replace('\\', '').replace('_', '\_').replace('%', '').strip()

		posts=posts.filter(
			or_(
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain),
				Submission.url.ilike("https://old." + domain)
				)
			)

	if search_operator_hole in criteria:
		posts = posts.filter(Submission.sub == criteria[search_operator_hole])

	if 'after' in criteria:
		after = int(criteria['after'])
		posts = posts.filter(Submission.created_utc > after)

	if 'before' in criteria:
		before = int(criteria['before'])
		posts = posts.filter(Submission.created_utc < before)

	posts = apply_time_filter(t, posts, Submission)

	posts = sort_posts(sort, posts)

	total = posts.count()

	posts = posts.offset(25 * (page - 1)).limit(26).all()

	ids = [x[0] for x in posts]




	next_exists = (len(ids) > 25)
	ids = ids[:25]

	posts = get_posts(ids, v=v)

	if request.headers.get("Authorization"): return {"total":total, "data":[x.json for x in posts]}

	return render_template("search.html",
						   v=v,
						   query=query,
						   total=total,
						   page=page,
						   listing=posts,
						   sort=sort,
						   t=t,
						   next_exists=next_exists
						   )

@app.get("/search/comments")
@auth_required
def searchcomments(v):


	query = request.values.get("q", '').strip()

	try: page = max(1, int(request.values.get("page", 1)))
	except: page = 1

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria = searchparse(query)

	comments = g.db.query(Comment.id).join(Comment.post) \
		.filter(Comment.parent_submission != None, Comment.author_id.notin_(v.userblocks))

	
	if 'post' in criteria:
		try: post = int(criteria['post'])
		except: return {"error": f"Post with id {post} does not exist."}
		comments = comments.filter(Comment.parent_submission == post)


	if 'author' in criteria:
		comments = comments.filter(Comment.ghost == False)
		author = get_user(criteria['author'])
		if not author: return {"error": "User not found"}
		if author.is_private and author.id != v.id and v.admin_level < 2 and not v.eye:
			if request.headers.get("Authorization"):
				return {"error": f"@{author.username}'s profile is private; You can't use the 'author' syntax on them"}

			return render_template("search_comments.html", v=v, query=query, total=0, page=page, comments=[], sort=sort, t=t, next_exists=False, error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them.")

		else: comments = comments.filter(Comment.author_id == author.id)

	if 'q' in criteria:
		words = [Comment.body.ilike('%'+x+'%') for x in criteria['q']]
		comments = comments.filter(*words)

	if 'over18' in criteria: comments = comments.filter(Comment.over_18 == True)

	if search_operator_hole in criteria:
		comments = comments.filter(Submission.sub == criteria[search_operator_hole])

	comments = apply_time_filter(t, comments, Comment)

	if v.admin_level < 2:
		private = [x[0] for x in g.db.query(Submission.id).filter(Submission.private == True).all()]

		comments = comments.filter(Comment.is_banned==False, Comment.deleted_utc == 0, Comment.parent_submission.notin_(private))


	if not v.paid_dues:
		club = [x[0] for x in g.db.query(Submission.id).filter(Submission.club == True).all()]
		comments = comments.filter(Comment.parent_submission.notin_(club))

	if 'after' in criteria:
		after = int(criteria['after'])
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = int(criteria['before'])
		comments = comments.filter(Comment.created_utc < before)

	comments = sort_comments(sort, comments)

	total = comments.count()

	comments = comments.offset(25 * (page - 1)).limit(26).all()

	ids = [x[0] for x in comments]

	next_exists = (len(ids) > 25)
	ids = ids[:25]

	comments = get_comments(ids, v=v)

	if request.headers.get("Authorization"): return {"total":total, "data":[x.json for x in comments]}
	return render_template("search_comments.html", v=v, query=query, total=total, page=page, comments=comments, sort=sort, t=t, next_exists=next_exists, standalone=True)


@app.get("/search/users")
@auth_required
def searchusers(v):

	query = request.values.get("q", '').strip()

	page = max(1, int(request.values.get("page", 1)))
	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()
	term=query.lstrip('@')
	term = term.replace('\\','').replace('_','\_').replace('%','')
	
	users=g.db.query(User).filter(
		or_(
			User.username.ilike(f'%{term}%'),
			User.original_username.ilike(f'%{term}%')
		)
	)
	
	if v.admin_level < 2:
		users = users.filter(User.shadowbanned == None)

	users=users.order_by(User.username.ilike(term).desc(), User.stored_subscriber_count.desc())
	
	total=users.count()
	
	users = users.offset(25 * (page-1)).limit(26).all()
	next_exists=(len(users)>25)
	users=users[:25]

	if request.headers.get("Authorization"): return {"data": [x.json for x in users]}
	return render_template("search_users.html", v=v, query=query, total=total, page=page, users=users, sort=sort, t=t, next_exists=next_exists)
