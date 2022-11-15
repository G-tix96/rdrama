import re

import requests

from files.classes.streamers import Streamer
from files.helpers.alerts import send_repeatable_notification
from files.helpers.const import *
from files.routes.wrappers import *
from files.__main__ import app, cache

id_regex = re.compile('"externalId":"([^"]*?)"', flags=re.A)
live_regex = re.compile('playerOverlayVideoDetailsRenderer":\{"title":\{"simpleText":"(.*?)"\},"subtitle":\{"runs":\[\{"text":"(.*?)"\},\{"text":" • "\},\{"text":"(.*?)"\}', flags=re.A)
live_thumb_regex = re.compile('\{"thumbnail":\{"thumbnails":\[\{"url":"(.*?)"', flags=re.A)
offline_regex = re.compile('","title":"(.*?)".*?"width":48,"height":48\},\{"url":"(.*?)"', flags=re.A)
offline_details_regex = re.compile('simpleText":"Streamed ([0-9]*?) ([^"]*?)"\},.*?"viewCountText":\{"simpleText":"([0-9,]*?) views"', flags=re.A)

def process_streamer(id, live='live'):
	url = f'https://www.youtube.com/channel/{id}/{live}'
	req = requests.get(url, cookies={'CONSENT': 'YES+1'}, timeout=5)
	text = req.text
	if '"videoDetails":{"videoId"' in text:
		y = live_regex.search(text)
		count = y.group(3)

		if count == '1 watching now':
			count = "1"

		if 'waiting' in count:
			if live != '':
				return process_streamer(id, '')
			else:
				return None

		count = int(count.replace(',', ''))

		t = live_thumb_regex.search(text)

		thumb = t.group(1)
		name = y.group(2)
		title = y.group(1)
		
		return (True, (id, req.url, thumb, name, title, count))
	else:
		t = offline_regex.search(text)
		if not t:
			if live != '':
				return process_streamer(id, '')
			else:
				return None

		y = offline_details_regex.search(text)

		if y:
			views = y.group(3).replace(',', '')
			quantity = int(y.group(1))
			unit = y.group(2)

			if unit.startswith('second'):
				modifier = 1/60
			elif unit.startswith('minute'):
				modifier = 1
			elif unit.startswith('hour'):
				modifier = 60
			elif unit.startswith('day'):
				modifier = 1440
			elif unit.startswith('week'):
				modifier = 10080
			elif unit.startswith('month'):
				modifier = 43800
			elif unit.startswith('year'):
				modifier = 525600

			minutes = quantity * modifier

			actual = f'{quantity} {unit}'
		else:
			minutes = 9999999999
			actual = '???'
			views = 0

		thumb = t.group(2)

		name = t.group(1)

		return (False, (id, req.url.rstrip('/live'), thumb, name, minutes, actual, views))


def live_cached():
	live = []
	offline = []
	db = db_session()
	streamers = [x[0] for x in db.query(Streamer.id).all()]
	db.close()
	for id in streamers:
		processed = process_streamer(id)
		if processed:
			if processed[0]: live.append(processed[1])
			else: offline.append(processed[1])

	live = sorted(live, key=lambda x: x[5], reverse=True)
	offline = sorted(offline, key=lambda x: x[4])

	if live: cache.set('live', live)
	if offline: cache.set('offline', offline)


@app.get('/live')
@auth_desired_with_logingate
def live_list(v):
	live = cache.get('live') or []
	offline = cache.get('offline') or []

	return render_template('live.html', v=v, live=live, offline=offline)

@app.post('/live/add')
@admin_level_required(PERMS['STREAMERS_MODERATION'])
def live_add(v):
	link = request.values.get('link').strip()

	if 'youtube.com/channel/' in link:
		id = link.split('youtube.com/channel/')[1].rstrip('/')
	else:
		text = requests.get(link, cookies={'CONSENT': 'YES+1'}, timeout=5).text
		try: id = id_regex.search(text).group(1)
		except: abort(400, "Invalid ID")

	live = cache.get('live') or []
	offline = cache.get('offline') or []

	if not id or len(id) != 24:
		abort(400, "Invalid ID")

	existing = g.db.get(Streamer, id)
	if not existing:
		streamer = Streamer(id=id)
		g.db.add(streamer)
		g.db.flush()
		if v.id != KIPPY_ID:
			send_repeatable_notification(KIPPY_ID, f"@{v.username} (Admin) has added a [new YouTube channel](https://www.youtube.com/channel/{streamer.id})")

		processed = process_streamer(id)
		if processed:
			if processed[0]: live.append(processed[1])
			else: offline.append(processed[1])

	live = sorted(live, key=lambda x: x[5], reverse=True)
	offline = sorted(offline, key=lambda x: x[4])

	if live: cache.set('live', live)
	if offline: cache.set('offline', offline)

	return redirect('/live')

@app.post('/live/remove')
@admin_level_required(PERMS['STREAMERS_MODERATION'])
def live_remove(v):
	id = request.values.get('id').strip()
	if not id: abort(400)
	streamer = g.db.get(Streamer, id)
	if streamer:
		if v.id != KIPPY_ID:
			send_repeatable_notification(KIPPY_ID, f"@{v.username} (Admin) has removed a [YouTube channel](https://www.youtube.com/channel/{streamer.id})")
		g.db.delete(streamer)

	live = cache.get('live') or []
	offline = cache.get('offline') or []

	live = [x for x in live if x[0] != id]
	offline = [x for x in offline if x[0] != id]

	if live: cache.set('live', live)
	if offline: cache.set('offline', offline)

	return redirect('/live')