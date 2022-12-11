import requests

from .config.const import *

def discord_message_send(channel_id, message):
	requests.post(
		f"https://discordapp.com/api/channels/{channel_id}/messages",
		headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
		data={"content": message},
		timeout=5)

def send_changelog_message(message):
	discord_message_send(DISCORD_CHANGELOG_CHANNEL_ID, message)

def send_wpd_message(message):
	discord_message_send(WPD_CHANNEL_ID, message)
