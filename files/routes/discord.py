from files.helpers.wrappers import *
from files.helpers.security import *
from files.helpers.discord import add_role
from files.__main__ import app
import requests


@app.get("/discord")
@is_not_permabanned
def join_discord(v):
	
	if v.shadowbanned: return {"error": "Internal server error"}, 400
	
	now=int(time.time())

	state=generate_hash(f"{now}+{v.id}+discord")

	state=f"{now}.{state}"

	return redirect(f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri=https%3A%2F%2F{SITE}%2Fdiscord_redirect&response_type=code&scope=identify%20guilds.join&state={state}")


@app.get("/discord_redirect")
@auth_required
def discord_redirect(v):


	now=int(time.time())
	state=request.values.get('state','').split('.')

	timestamp=state[0]

	state=state[1]

	if int(timestamp) < now-600:
		abort(400)

	if not validate_hash(f"{timestamp}+{v.id}+discord", state):
		abort(400)

	code = request.values.get("code","")
	if not code:
		abort(400)

	data={
		"client_id": DISCORD_CLIENT_ID,
		'client_secret': DISCORD_CLIENT_SECRET,
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': f"https://{SITE}/discord_redirect",
		'scope': 'identify guilds.join'
	}
	headers={
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	url="https://discord.com/api/oauth2/token"

	x=requests.post(url, headers=headers, data=data, timeout=5)

	x=x.json()


	token=x["access_token"]


	url="https://discord.com/api/users/@me"
	headers={
		'Authorization': f"Bearer {token}"
	}
	x=requests.get(url, headers=headers, timeout=5)

	x=x.json()



	headers={
		'Authorization': f"Bot {DISCORD_BOT_TOKEN}",
		'Content-Type': "application/json"
	}

	if v.discord_id and v.discord_id != x['id']:
		url=f"https://discord.com/api/guilds/{DISCORD_SERVER_ID}/members/{v.discord_id}"
		requests.delete(url, headers=headers, timeout=5)

	if g.db.query(User).filter(User.id!=v.id, User.discord_id==x["id"]).one_or_none():
		return render_template("message.html", title="Discord account already linked.", error="That Discord account is already in use by another user.", v=v)

	v.discord_id=x["id"]
	g.db.add(v)

	url=f"https://discord.com/api/guilds/{DISCORD_SERVER_ID}/members/{x['id']}"

	name=v.username

	data={
		"access_token":token,
		"nick":name,
	}

	x=requests.put(url, headers=headers, json=data, timeout=5)

	if x.status_code in {201, 204}:
		time.sleep(0.1)
		add_role(v, "linked")

		if v.patron:
			time.sleep(0.1)
			add_role(v, str(v.patron))

		if SITE == 'rdrama.net' and v.id == AEVANN_ID:
			time.sleep(0.1)
			add_role(v, "admin")

			time.sleep(0.1)
			requests.put("https://discord.com/api/guilds/913091440035389520/members/788152118669606932", headers=headers, json={"access_token":token,"roles":[915260962540511292]}, timeout=5)
	else:
		return x.json()


	if x.status_code==204:

		url=f"https://discord.com/api/guilds/{DISCORD_SERVER_ID}/members/{v.discord_id}"
		data={
			"nick": name
		}

		requests.patch(url, headers=headers, json=data, timeout=5)


	return redirect(f"https://discord.com/channels/{DISCORD_SERVER_ID}/{DISCORD_WELCOME_CHANNEL}")