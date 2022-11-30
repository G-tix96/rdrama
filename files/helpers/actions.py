import random
import time
from urllib.parse import quote

import gevent
import requests
from flask import g
from files.classes.flags import Flag
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification

from files.helpers.alerts import send_repeatable_notification
from files.helpers.const import *
from files.helpers.const_stateful import *
from files.helpers.discord import discord_message_send
from files.helpers.get import *
from files.helpers.sanitize import *
from files.helpers.settings import get_setting
from files.helpers.slots import check_slots_command


def _archiveorg(url):
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	try:
		requests.get(f'https://web.archive.org/save/{url}',
			headers=headers, timeout=10, proxies=proxies)
	except: pass
	try:
		requests.post('https://ghostarchive.org/archive2', data={"archive": url},
			headers=headers, timeout=10, proxies=proxies)
	except: pass


def archive_url(url):	
	gevent.spawn(_archiveorg, url)
	if url.startswith('https://twitter.com/'):
		url = url.replace('https://twitter.com/', 'https://nitter.lacontrevoie.fr/')
		gevent.spawn(_archiveorg, url)
	if url.startswith('https://instagram.com/'):
		url = url.replace('https://instagram.com/', 'https://imginn.com/')
		gevent.spawn(_archiveorg, url)

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
	elif post.sub == 'masterbaiters' and random.random() < 0.33:
		body = "Can you people come up with any ideas that don't involve committing federal crimes"
	else:
		if SNAPPY_MARSEYS and SNAPPY_QUOTES:
			if random.random() < 0.5: SNAPPY_CHOICES = SNAPPY_MARSEYS
			else: SNAPPY_CHOICES = SNAPPY_QUOTES
		elif SNAPPY_MARSEYS: SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_QUOTES: SNAPPY_CHOICES = SNAPPY_QUOTES
		else: SNAPPY_CHOICES = [""]

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
		elif body.startswith('▲') or body.startswith(':#marseyupvote'):
			body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=1,
						submission_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.upvotes += 1
		elif body == '!slots':
			body = f'!slots{snappy.coins}'

	body += "\n\n"

	if post.url and not post.url.startswith(SITE_FULL) and not post.url.startswith('/') and not post.url.startswith(f'https://{BAN_EVASION_DOMAIN}'):
		if post.url.startswith('https://old.reddit.com/r/'):
			rev = post.url.replace('https://old.reddit.com/', '')
			rev = f"* [unddit.com](https://unddit.com/{rev})\n"
		elif post.url.startswith("https://old.reddit.com/u/"):
			rev = post.url.replace('https://old.reddit.com/u/', '')
			rev = f"* [camas.unddit.com](https://camas.unddit.com/reddit-search/#\u007b\"author\":\"{rev}\",\"resultSize\":100\u007d)\n"
		else: rev = ''

		body += f"Snapshots:\n\n{rev}* [archive.org](https://web.archive.org/{post.url})\n* [ghostarchive.org](https://ghostarchive.org/search?term={quote(post.url)})\n* [archive.ph](https://archive.ph/?url={quote(post.url)}&run=1) (click to archive)\n\n"
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
		if href.startswith(SITE_FULL) or href.startswith(f'https://{BAN_EVASION_DOMAIN}'): continue
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
			addition += f'* [ghostarchive.org](https://ghostarchive.org/search?term={quote(href)})\n'
			addition += f'* [archive.ph](https://archive.ph/?url={quote(href)}&run=1) (click to archive)\n'
			addition += '\n'
			if len(f'{body}{addition}') > COMMENT_BODY_LENGTH_LIMIT: break
			body += addition
			archive_url(href)

	body = body.strip()[:COMMENT_BODY_LENGTH_LIMIT]
	body_html = sanitize(body)

	if len(body_html) == 0:
		return

	if len(body_html) < COMMENT_BODY_HTML_LENGTH_LIMIT:
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

		check_slots_command(v, snappy, c)

		snappy.comment_count += 1
		snappy.pay_account('coins', 1)
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
			note = f'duration: {duration}, reason: "{reason}"'
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
		body_html='<p class="zozbot">zoz</p>',
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
		body_html='<p class="zozbot">zle</p>',
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
		body_html='<p class="zozbot">zozzle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c4)

	zozbot = get_account(ZOZBOT_ID)
	zozbot.comment_count += 3
	zozbot.pay_account('coins', 1)
	g.db.add(zozbot)

def execute_longpostbot(c, level, body, body_html, parent_submission, v):
	if not len(c.body.split()) >= 200: return
	if "</blockquote>" in body_html: return
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
	longpostbot.pay_account('coins', 1)
	g.db.add(longpostbot)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

def execute_basedbot(c, level, body, parent_post, v):
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
		parent_submission=parent_post.id,
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

def execute_antispam_submission_check(title, v, url):
	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_posts = g.db.query(Submission).filter(
					Submission.author_id == v.id,
					Submission.title.op('<->')(title) < SPAM_SIMILARITY_THRESHOLD,
					Submission.created_utc > cutoff
	).all()

	if url:
		similar_urls = g.db.query(Submission).filter(
					Submission.author_id == v.id,
					Submission.url.op('<->')(url) < SPAM_URL_SIMILARITY_THRESHOLD,
					Submission.created_utc > cutoff
		).all()
	else: similar_urls = []

	threshold = SPAM_SIMILAR_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7): threshold *= 3
	elif v.age >= (60 * 60 * 24): threshold *= 2

	if max(len(similar_urls), len(similar_posts)) >= threshold:
		text = "Your account has been banned for **1 day** for the following reason:\n\n> Too much spam!"
		send_repeatable_notification(v.id, text)

		v.ban(reason="Spamming.",
			  days=1)

		for post in similar_posts + similar_urls:
			post.is_banned = True
			post.is_pinned = False
			post.ban_reason = "AutoJanny"
			g.db.add(post)
			ma=ModAction(
					user_id=AUTOJANNY_ID,
					target_submission_id=post.id,
					kind="ban_post",
					_note="spam"
					)
			g.db.add(ma)
		return False
	return True

def execute_blackjack_custom(v, target, body, type):
	return True

def execute_blackjack(v, target, body, type):
	if not execute_blackjack_custom(v, target, body, type): return False
	if not blackjack or not body: return True
	if any(i in body.lower() for i in blackjack.split()):
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = f"Blackjack"
		g.db.add(v)
		notif = None
		extra_info = "unknown entity"
		if type == 'submission':
			extra_info = f"submission ({target.permalink})"
		elif type == 'comment' or type == 'message':
			extra_info = f"{type} ({target.permalink})"
			notif = Notification(comment_id=target.id, user_id=CARP_ID)
		elif type == 'chat':
			extra_info = "chat message"
		elif type == 'flag':
			extra_info = f"reports on {target.permalink}"
		elif type == 'modmail':
			extra_info = "modmail"

		if notif:
			g.db.add(notif)
			g.db.flush()
		elif extra_info: send_repeatable_notification(CARP_ID, f"Blackjack for {v.username}: {extra_info}")
		return False
	return True

def execute_antispam_duplicate_comment_check(v:User, body_html:str):
	'''
	Sanity check for newfriends
	'''
	ANTISPAM_DUPLICATE_THRESHOLD = 3
	if v.id in ANTISPAM_BYPASS_IDS or v.admin_level: return
	if v.age >= NOTIFICATION_SPAM_AGE_THRESHOLD: return
	if len(body_html) < 16: return
	if body_html == '!wordle': return # wordle
	compare_time = int(time.time()) - 60 * 60 * 24
	count = g.db.query(Comment.id).filter(Comment.body_html == body_html,
										  Comment.created_utc >= compare_time).count()
	if count <= ANTISPAM_DUPLICATE_THRESHOLD: return
	v.ban(reason="Spamming.", days=0.0)
	send_repeatable_notification(v.id, "Your account has been banned **permanently** for the following reason:\n\n> Too much spam!")
	g.db.add(v)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_antispam_comment_check(body:str, v:User):
	if v.id in ANTISPAM_BYPASS_IDS: return
	if len(body) <= COMMENT_SPAM_LENGTH_THRESHOLD: return
	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_comments = g.db.query(Comment).filter(
		Comment.author_id == v.id,
		Comment.body.op('<->')(body) < COMMENT_SPAM_SIMILAR_THRESHOLD,
		Comment.created_utc > cutoff
	).all()

	threshold = COMMENT_SPAM_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7):
		threshold *= 3
	elif v.age >= (60 * 60 * 24):
		threshold *= 2

	if len(similar_comments) <= threshold: return
	text = "Your account has been banned for **1 day** for the following reason:\n\n> Too much spam!"
	send_repeatable_notification(v.id, text)
	v.ban(reason="Spamming.",
			days=1)
	for comment in similar_comments:
		comment.is_banned = True
		comment.ban_reason = "AutoJanny"
		g.db.add(comment)
		ma=ModAction(
			user_id=AUTOJANNY_ID,
			target_comment_id=comment.id,
			kind="ban_comment",
			_note="spam"
		)
		g.db.add(ma)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_under_siege(v:User, target:Optional[Union[Submission, Comment]], body, type:str):
	if not get_setting("under_siege"): return True
	if v.age < UNDER_SIEGE_AGE_THRESHOLD and not v.admin_level >= PERMS['SITE_BYPASS_UNDER_SIEGE_MODE']:
		v.shadowbanned = 'AutoJanny'
		if not v.is_banned: v.ban_reason = f"Under Siege"
		v.is_muted = True
		g.db.add(v)
		with open(f"/under_siege.log", "a", encoding="utf-8") as f:
			t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
			f.write(f"[{t}] {v.id} @{v.username} {type} {v.age}s\n")
		discord_message_send(UNDER_SIEGE_CHANNEL_ID,
			f"<{SITE_FULL}/id/{v.id}> `@{v.username} {type} {v.age}s`")
		return False
	return True

def execute_lawlz_actions(v:User, p:Submission):
	if v.id != LAWLZ_ID: return
	if SITE_NAME != 'rDrama': return
	if not FEATURES['PINS']: return
	p.stickied_utc = int(time.time()) + 86400
	p.stickied = AUTOJANNY_ID
	p.distinguish_level = 6
	p.flair = filter_emojis_only(":ben10: Required Reading")
	pin_time = 'for 1 day'
	ma_1=ModAction(
		kind="pin_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id,
		_note=pin_time
	)
	ma_2=ModAction(
		kind="distinguish_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id
	)
	ma_3=ModAction(
		kind="flair_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id,
		_note=f'"{p.flair}"'
	)
	g.db.add(p)
	g.db.add(ma_1)
	g.db.add(ma_2)
	g.db.add(ma_3)
