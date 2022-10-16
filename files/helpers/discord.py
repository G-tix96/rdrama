import requests

from .const import *

headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

def send_changelog_message(message):
	data={"content": message}
	for id in DISCORD_CHANGELOG_CHANNEL_IDS:
		requests.post(f"https://discordapp.com/api/channels/{id}/messages", headers=headers, data=data, timeout=5)

def send_wpd_message(message):
	data={"content": message}
	requests.post(f"https://discordapp.com/api/channels/{WPD_CHANNEL_ID}/messages", headers=headers, data=data, timeout=5)
