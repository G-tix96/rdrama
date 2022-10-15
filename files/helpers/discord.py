import requests
import threading
from .const import *

headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

def discord_wrap(f):

	def wrapper(*args, **kwargs):

		user=args[0]
		if not user.discord_id:
			return


		thread=threading.Thread(target=f, args=args, kwargs=kwargs)
		thread.start()

	wrapper.__name__=f.__name__
	return wrapper



@discord_wrap
def add_role(user, role_name):
	role_id = ROLES[role_name]
	url = f"https://discordapp.com/api/guilds/{DISCORD_SERVER_ID}/members/{user.discord_id}/roles/{role_id}"
	requests.put(url, headers=headers, timeout=5)

@discord_wrap
def remove_role(user, role_name):
	role_id = ROLES[role_name]
	url = f"https://discordapp.com/api/guilds/{DISCORD_SERVER_ID}/members/{user.discord_id}/roles/{role_id}"
	requests.delete(url, headers=headers, timeout=5)

@discord_wrap
def remove_user(user):
	url=f"https://discordapp.com/api/guilds/{DISCORD_SERVER_ID}/members/{user.discord_id}"
	requests.delete(url, headers=headers, timeout=5)

@discord_wrap
def set_nick(user, nick):
	url=f"https://discordapp.com/api/guilds/{DISCORD_SERVER_ID}/members/{user.discord_id}"
	data={"nick": nick}
	requests.patch(url, headers=headers, json=data, timeout=5)

def send_changelog_message(message):
	data={"content": message}
	for id in DISCORD_CHANGELOG_CHANNEL_IDS:
		requests.post(f"https://discordapp.com/api/channels/{id}/messages", headers=headers, data=data, timeout=5)

def send_wpd_message(message):
	data={"content": message}
	requests.post(f"https://discordapp.com/api/channels/{WPD_CHANNEL_ID}/messages", headers=headers, data=data, timeout=5)
