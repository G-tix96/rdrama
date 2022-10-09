from flask import g
from files.classes.badges import Badge
from files.helpers.alerts import send_repeatable_notification
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.sanitize import *
import random
from urllib.parse import quote

def badge_grant(user, badge_id, description=None, url=None, notify=True):
	assert user != None
	if user.has_badge(badge_id):
		return

	badge = Badge(
		badge_id=int(badge_id),
		user_id=user.id,
		description=description,
		url=url,
	)

	g.db.add(badge)
	g.db.flush()

	if notify:
		send_repeatable_notification(user.id,
			f"@AutoJanny has given you the following profile badge:\n\n" +
			f"![]({badge.path})\n\n**{badge.name}**\n\n{badge.badge.description}")


def archiveorg(url):
	try: requests.get(f'https://web.archive.org/save/{url}', headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}, timeout=100)
	except: pass

def archive_url(url):	
	gevent.spawn(archiveorg, url)
	if url.startswith('https://twitter.com/'):
		url = url.replace('https://twitter.com/', 'https://nitter.lacontrevoie.fr/')
		gevent.spawn(archiveorg, url)
	if url.startswith('https://instagram.com/'):
		url = url.replace('https://instagram.com/', 'https://imginn.com/')
		gevent.spawn(archiveorg, url)


def execute_snappy(post, v):
	snappy = get_account(SNAPPY_ID)

	if post.sub == 'dankchristianmemes' or post.sub == 'truth':
		body = random.choice(christian_emojis)
	elif v.id == CARP_ID:
		if random.random() < 0.02: body = "i love you carp"
		elif random.random() < 0.02: body = "![](/images/16614707883108485.webp)"
		else: body = ":#marseyfuckoffcarp:"
	elif v.id == LAWLZ_ID:
		if random.random() < 0.5: body = "wow, this lawlzpost sucks!"
		else: body = "wow, a good lawlzpost for once!"
	elif not SNAPPY_MARSEYS and not SNAPPY_QUOTES:
		body = ""
	else:
		if SNAPPY_MARSEYS and SNAPPY_QUOTES:
			if random.random() < 0.5: SNAPPY_CHOICES = SNAPPY_MARSEYS
			else: SNAPPY_CHOICES = SNAPPY_QUOTES
		elif SNAPPY_MARSEYS: SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_QUOTES: SNAPPY_CHOICES = SNAPPY_QUOTES

		body = random.choice(SNAPPY_CHOICES).strip()
		if body.startswith('▼'):
			body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=-1,
						submission_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.downvotes += 1
			if body.startswith('OP is a Trump supporter'):
				flag = Flag(post_id=post.id, user_id=SNAPPY_ID, reason='Trump supporter')
				g.db.add(flag)
			elif body.startswith('You had your chance. Downvoted and reported'):
				flag = Flag(post_id=post.id, user_id=SNAPPY_ID, reason='Retard')
				g.db.add(flag)
		elif body.startswith('▲'):
			body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=1,
						submission_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.upvotes += 1

	body += "\n\n"

	if post.url and not post.url.startswith(SITE_FULL) and not post.url.startswith('/') and not post.url.startswith('https://rdrama.org/'):
		if post.url.startswith('https://old.reddit.com/r/'):
			rev = post.url.replace('https://old.reddit.com/', '')
			rev = f"* [unddit.com](https://unddit.com/{rev})\n"
		elif post.url.startswith("https://old.reddit.com/u/"):
			rev = post.url.replace('https://old.reddit.com/u/', '')
			rev = f"* [camas.unddit.com](https://camas.unddit.com/reddit-search/#\u007b\"author\":\"{rev}\",\"resultSize\":100\u007d)\n"
		else: rev = ''
		
		body += f"Snapshots:\n\n{rev}* [archive.org](https://web.archive.org/{post.url})\n* [archive.ph](https://archive.ph/?url={quote(post.url)}&run=1) (click to archive)\n* [ghostarchive.org](https://ghostarchive.org/search?term={quote(post.url)}) (click to archive)\n\n"
		archive_url(post.url)

	captured = []
	body_for_snappy = post.body_html.replace(' data-src="', ' src="')


	for i in list(snappy_url_regex.finditer(body_for_snappy)):
		href = i.group(1)
		if href in [x[0] for x in captured]: continue
		title = i.group(2)
		captured.append((href, title))

	for i in list(snappy_youtube_regex.finditer(body_for_snappy)):
		href = f'https://youtube.com/watch?v={i.group(1)}'
		if href in [x[0] for x in captured]: continue
		captured.append((href, href))


	for href, title in captured:
		if href.startswith(SITE_FULL) or href.startswith('https://rdrama.org/'): continue

		if "Snapshots:\n\n" not in body: body += "Snapshots:\n\n"

		if f'**[{title}]({href})**:\n\n' not in body:
			addition = f'**[{title}]({href})**:\n\n'
			if href.startswith('https://old.reddit.com/r/'):
				rev = href.replace('https://old.reddit.com/', '')
				addition += f'* [unddit.com](https://unddit.com/{rev})\n'
			if href.startswith('https://old.reddit.com/u/'):
				rev = href.replace('https://old.reddit.com/u/', '')
				addition += f"* [camas.unddit.com](https://camas.unddit.com/reddit-search/#\u007b\"author\":\"{rev}\",\"resultSize\":100\u007d)\n"
			addition += f'* [archive.org](https://web.archive.org/{href})\n'
			addition += f'* [archive.ph](https://archive.ph/?url={quote(href)}&run=1) (click to archive)\n'
			addition += f'* [ghostarchive.org](https://ghostarchive.org/search?term={quote(href)}) (click to archive)\n\n'
			if len(f'{body}{addition}') > 10000: break
			body += addition
			archive_url(href)

	body = body.strip()[:POST_BODY_LENGTH_LIMIT]
	body_html = sanitize(body)

	if len(body_html) == 0:
		return

	if len(body_html) < POST_BODY_HTML_LENGTH_LIMIT:
		c = Comment(author_id=SNAPPY_ID,
			distinguish_level=6,
			parent_submission=post.id,
			level=1,
			over_18=False,
			is_bot=True,
			app_id=None,
			body=body,
			body_html=body_html,
			ghost=post.ghost
			)

		g.db.add(c)

		snappy.comment_count += 1
		snappy.coins += 1
		g.db.add(snappy)

		if FEATURES['PINS'] and (body.startswith(':#marseypin:') or body.startswith(':#marseypin2:')):
			post.stickied = "Snappy"
			post.stickied_utc = int(time.time()) + 3600

		elif SITE_NAME == 'rDrama' and body.startswith(':#marseyban:'):
			days = 0.01
			reason = f'<a href="/post/{post.id}">/post/{post.id}</a>'
			v.ban(admin=snappy, reason=reason, days=days)
			text = f"@Snappy has banned you for **{days}** days for the following reason:\n\n> {reason}"
			send_repeatable_notification(v.id, text)
			duration = f"for {days} days"
			note = f'reason: "{reason}", duration: {duration}'
			ma=ModAction(
				kind="ban_user",
				user_id=snappy.id,
				target_user_id=v.id,
				_note=note
				)
			g.db.add(ma)
			post.bannedfor = f'{duration} by @Snappy'

		g.db.flush()

		c.top_comment_id = c.id

		post.comment_count += 1
		post.replies = [c]

def execute_zozbot(c, level, parent_submission, v):
	if random.random() >= 0.001: return
	c2 = Comment(author_id=ZOZBOT_ID,
		parent_submission=parent_submission,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body="zoz",
		body_html="<p>zoz</p>",
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c2)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

	c3 = Comment(author_id=ZOZBOT_ID,
		parent_submission=parent_submission,
		parent_comment_id=c2.id,
		level=level+2,
		is_bot=True,
		body="zle",
		body_html="<p>zle</p>",
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c3)
	g.db.flush()
		

	c4 = Comment(author_id=ZOZBOT_ID,
		parent_submission=parent_submission,
		parent_comment_id=c3.id,
		level=level+3,
		is_bot=True,
		body="zozzle",
		body_html="<p>zozzle</p>",
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c4)

	zozbot = get_account(ZOZBOT_ID)
	zozbot.comment_count += 3
	zozbot.coins += 3
	g.db.add(zozbot)

def execute_longpostbot(c, level, body, body_html, parent_submission, v):
	if not len(c.body.split()) >= 200: return
	if "<" in body and "</blockquote>" in body_html: return
	body = random.choice(LONGPOST_REPLIES)
	if body.startswith('▼'):
		body = body[1:]
		vote = CommentVote(user_id=LONGPOSTBOT_ID,
			vote_type=-1,
			comment_id=c.id,
			real = True
		)
		g.db.add(vote)
		c.downvotes = 1

	c2 = Comment(author_id=LONGPOSTBOT_ID,
		parent_submission=parent_submission,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body=body,
		body_html=f"<p>{body}</p>",
		top_comment_id=c.top_comment_id,
		ghost=c.ghost
	)

	g.db.add(c2)

	longpostbot = get_account(LONGPOSTBOT_ID)
	longpostbot.comment_count += 1
	longpostbot.coins += 1
	g.db.add(longpostbot)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

def execute_basedbot(c, level, body, parent_submission, parent_post, v):
	pill = based_regex.match(body)
	if level == 1: basedguy = get_account(parent_post.author_id)
	else: basedguy = get_account(c.parent_comment.author_id)
	basedguy.basedcount += 1
	if pill:
		if basedguy.pills: basedguy.pills += f", {pill.group(1)}"
		else: basedguy.pills += f"{pill.group(1)}"
	g.db.add(basedguy)

	body2 = f"@{basedguy.username}'s Based Count has increased by 1. Their Based Count is now {basedguy.basedcount}."
	if basedguy.pills: body2 += f"\n\nPills: {basedguy.pills}"
	
	body_based_html = sanitize(body2)
	c_based = Comment(author_id=BASEDBOT_ID,
		parent_submission=parent_submission,
		distinguish_level=6,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body_html=body_based_html,
		top_comment_id=c.top_comment_id,
		ghost=c.ghost
	)

	g.db.add(c_based)
	g.db.flush()

	n = Notification(comment_id=c_based.id, user_id=v.id)
	g.db.add(n)
