import random
from datetime import date
from .get import get_or_create_event_user

def user_event_darkmode(target, db):
	user = get_or_create_event_user(target, db)
	return user.event_darkmode

EVENT_JINJA_CONST = {
	"EVENT_BANNER": "banner_rDrama.html",
	"EVENT_ICONS": True,
	"EVENT_SIDEBAR": True,
	"EVENT_STYLES": "blizzard.css",
	"EVENT_AWARDS": True,
	"EVENT_MUSIC": "music.html",
	"EVENT_VISITORS_HERE_FLAVOR": [
		' santa enjoyers kissing under a misletoe',
		' bringing up family drama at Christmas dinner',
		' least homoerotic dramanauts stroking their candy canes',
		" dramanauts jingling each other's balls",
		" average Santa deniers getting reamed by Rudolph the Red-Nosed Reindeer",
		" naughty listers getting coal for fistmas",
		" plus-sized dramanauts eating Santa's cookies",
		" dramatards having their chimneys stuffed by Santa",
	],
	"random": random,
	"user_event_darkmode": user_event_darkmode,
}
