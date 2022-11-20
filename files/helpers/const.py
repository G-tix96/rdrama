from copy import deepcopy
from os import environ, path

import tldextract

DEFAULT_CONFIG_VALUE = "blahblahblah"
SITE = environ.get("SITE", "localhost").strip()
SITE_NAME = environ.get("SITE_NAME", "rdrama.net").strip()
SECRET_KEY = environ.get("SECRET_KEY", DEFAULT_CONFIG_VALUE).strip()
PROXY_URL = environ.get("PROXY_URL", "http://localhost:18080").strip()
GIPHY_KEY = environ.get("GIPHY_KEY", DEFAULT_CONFIG_VALUE).strip()
DISCORD_BOT_TOKEN = environ.get("DISCORD_BOT_TOKEN", DEFAULT_CONFIG_VALUE).strip()
TURNSTILE_SITEKEY = environ.get("TURNSTILE_SITEKEY", DEFAULT_CONFIG_VALUE).strip()
TURNSTILE_SECRET = environ.get("TURNSTILE_SECRET", DEFAULT_CONFIG_VALUE).strip()
YOUTUBE_KEY = environ.get("YOUTUBE_KEY", DEFAULT_CONFIG_VALUE).strip()
PUSHER_ID = environ.get("PUSHER_ID", DEFAULT_CONFIG_VALUE).strip()
PUSHER_KEY = environ.get("PUSHER_KEY", DEFAULT_CONFIG_VALUE).strip()
IMGUR_KEY = environ.get("IMGUR_KEY", DEFAULT_CONFIG_VALUE).strip()
SPAM_SIMILARITY_THRESHOLD = float(environ.get("SPAM_SIMILARITY_THRESHOLD", "0.5").strip())
SPAM_URL_SIMILARITY_THRESHOLD = float(environ.get("SPAM_URL_SIMILARITY_THRESHOLD", "0.1").strip())
SPAM_SIMILAR_COUNT_THRESHOLD = int(environ.get("SPAM_SIMILAR_COUNT_THRESHOLD", "10").strip())
COMMENT_SPAM_SIMILAR_THRESHOLD = float(environ.get("COMMENT_SPAM_SIMILAR_THRESHOLD", "0.5").strip())
COMMENT_SPAM_COUNT_THRESHOLD = int(environ.get("COMMENT_SPAM_COUNT_THRESHOLD", "10").strip())
DEFAULT_TIME_FILTER = environ.get("DEFAULT_TIME_FILTER", "all").strip()
GUMROAD_TOKEN = environ.get("GUMROAD_TOKEN", DEFAULT_CONFIG_VALUE).strip()
GUMROAD_LINK = environ.get("GUMROAD_LINK", DEFAULT_CONFIG_VALUE).strip()
GUMROAD_ID = environ.get("GUMROAD_ID", DEFAULT_CONFIG_VALUE).strip()
DISABLE_DOWNVOTES = bool(int(environ.get("DISABLE_DOWNVOTES", "0").strip()))
DUES = int(environ.get("DUES", "0").strip())
DEFAULT_THEME = environ.get("DEFAULT_THEME", "midnight").strip()
DEFAULT_COLOR = environ.get("DEFAULT_COLOR", "805ad5").strip()
CARD_VIEW = bool(int(environ.get("CARD_VIEW", "0").strip()))
EMAIL = environ.get("EMAIL", "blahblahblah@gmail.com").strip()
MAILGUN_KEY = environ.get("MAILGUN_KEY", DEFAULT_CONFIG_VALUE).strip()
DESCRIPTION = environ.get("DESCRIPTION", "rdrama.net caters to drama in all forms such as: Real life, videos, photos, gossip, rumors, news sites, Reddit, and Beyond™. There isn't drama we won't touch, and we want it all!").strip()
CF_KEY = environ.get("CF_KEY", DEFAULT_CONFIG_VALUE).strip()
CF_ZONE = environ.get("CF_ZONE", DEFAULT_CONFIG_VALUE).strip()
TELEGRAM_LINK = environ.get("TELEGRAM_LINK", DEFAULT_CONFIG_VALUE).strip()
GLOBAL = environ.get("GLOBAL", "").strip()
blackjack = environ.get("BLACKJACK", "").strip()
FP = environ.get("FP", "").strip()
KOFI_TOKEN = environ.get("KOFI_TOKEN", "").strip()
KOFI_LINK = environ.get("KOFI_LINK", "").strip()

PUSHER_ID_CSP = ""
if PUSHER_ID != DEFAULT_CONFIG_VALUE:
	PUSHER_ID_CSP = f" {PUSHER_ID}.pushnotifications.pusher.com"
CONTENT_SECURITY_POLICY_DEFAULT = "script-src 'self' 'unsafe-inline' challenges.cloudflare.com; connect-src 'self'; object-src 'none';"
CONTENT_SECURITY_POLICY_HOME = f"script-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src 'self' tls-use1.fpapi.io api.fpjs.io{PUSHER_ID_CSP}; object-src 'none';"

CLOUDFLARE_COOKIE_VALUE = "yes." # remember to change this in CloudFlare too

SETTINGS_FILENAME = '/site_settings.json'

DEFAULT_RATELIMIT = "3/second;30/minute;200/hour;1000/day"
DEFAULT_RATELIMIT_SLOWER = "1/second;30/minute;200/hour;1000/day"
DEFAULT_RATELIMIT_USER = DEFAULT_RATELIMIT_SLOWER

PUSHER_LIMIT = 1000 # API allows 10 KB but better safe than sorry

IS_LOCALHOST = SITE == "localhost" or SITE == "127.0.0.1" or SITE.startswith("192.168.")

if IS_LOCALHOST: SITE_FULL = 'http://' + SITE
else: SITE_FULL = 'https://' + SITE


if SITE_NAME == 'PCM': CC = "SPLASH MOUNTAIN"
else: CC = "COUNTRY CLUB"
CC_TITLE = CC.title()

CASINO_RELEASE_DAY = 1662825600

if SITE_NAME == 'rDrama': patron = 'Paypig'
else: patron = 'Patron'

AJ_REPLACEMENTS = {
	' your ': " you're ",
	' to ': " too ", 

	' Your ': " You're ",
	' To ': " Too ",

	' YOUR ': " YOU'RE ",
	' TO ': " TOO ",

	'everyone': 'everypony',
	'everybody': 'everypony',

	'Everyone': 'Everypony',
	'Everybody': 'Everypony',

	'EVERYONE': 'EVERYPONY',
	'EVERYBODY': 'EVERYPONY',
}

SLURS = {
	"nigger": "BIPOC",
	"niglet": 'BIPOClet',
	"negress": "BIPOC woman",
	'nigga': 'neighbor',
	"faggot": "cute twink",
	"fag": "strag",
	"spic ": "hard-working American ",
	"spics": "hard-working Americans",
	"trannie": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"tranny": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"troon": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"kike": "jewish chad",
	"daisy's destruction": "Cars 2",
	"daisys destruction": "Cars 2",
	"daisy destruction": "Cars 2",
}

if SITE_NAME == 'rDrama':
	RDRAMA_SLURS = {
		"retarded": "r-slurred",
		"retard": "r-slur",
		"pedophile": "libertarian",
		"kill youself": "keep yourself safe",
		"kill yourself": "keep yourself safe",
		"kill yourselves": "keep yourselves safe",
		"steve akins": "Dr. Penelope Verity Oaken",
		"steve joel akins": "Dr. Penelope Verity Oaken",
		"steven joel akins": "Dr. Penelope Verity Oaken",
		"latinos": "latinx",
		"latino": "latinx",
		"latinas": "latinx",
		"latina": "latinx",
		"hispanics": "latinx",
		"hispanic": "latinx",
		"i hate marsey": "i love marsey",
		"sodomite": "total dreamboat",
		"pajeet": "sexy Indian dude",
		"renter": "rentoid",
		"autistic": "neurodivergent",
		"i hate carp": "i love Carp",
		"gamer": "g*mer",
		"journalist": "journ*list",
		"journalism": "journ*lism",
		"elon musk": "rocket daddy",
		"fake and gay": "fake and straight",
		" rapist": " male feminist",
		" pedo ": " libertarian ",
		" kys": " keep yourself safe",
		"kys ": "keep yourself safe ",
		"republican": 'republiKKKan',
		"america": 'ameriKKKa',
	}
	SLURS.update(RDRAMA_SLURS)

PROFANITIES = {
	'motherfucker': 'motherlover',
	'fuck': 'frick',
	' ass ': ' butt ',
	'shitting': 'pooping',
	'lmao': 'lmbo',
	'damn': 'darn',
	'bastard': 'fatherless child',
	'bitch': 'b-word',
	'toilet': 'potty',
	' asshole': ' butthole',
	' rape ': ' r*pe ',
	' hell ': ' heck ',
	' sex ': ' intercourse ',
	' cum ': ' c*m ',
	'orgasm': 'sexual climax',
	'dick': 'peepee',
	'cock ': 'peepee ',
	'cocks': 'peepees',
	'penis': 'peepee',
	'pussy': 'girl peepee',
	'vagina': 'girl peepee',
	' twat': ' girl peepee',
}

slur_single_words = "|".join([slur.lower() for slur in SLURS.keys()])
profanity_single_words = "|".join([profanity.lower() for profanity in PROFANITIES.keys()])

LONGPOST_REPLIES = ('Wow, you must be a JP fan.', 'This is one of the worst posts I have EVER seen. Delete it.', "No, don't reply like this, please do another wall of unhinged rant please.", '<h1>😴😴😴</h1>', "Ma'am we've been over this before. You need to stop.", "I've known more coherent downies.", "Your pulitzer's in the mail", "That's great and all, but I asked for my burger without cheese.", 'That degree finally paying off', "That's nice sweaty. Why don't you have a seat in the time out corner with Pizzashill until you calm down, then you can have your Capri Sun.", "All them words won't bring your pa back.", "You had a chance to not be completely worthless, but it looks like you threw it away. At least you're consistent.", 'Some people are able to display their intelligence by going on at length on a subject and never actually saying anything. This ability is most common in trades such as politics, public relations, and law. You have impressed me by being able to best them all, while still coming off as an absolute idiot.', "You can type 10,000 characters and you decided that these were the one's that you wanted.", 'Have you owned the libs yet?', "I don't know what you said, because I've seen another human naked.", 'Impressive. Normally people with such severe developmental disabilities struggle to write much more than a sentence or two. He really has exceded our expectations for the writing portion. Sadly the coherency of his writing, along with his abilities in the social skills and reading portions, are far behind his peers with similar disabilities.', "This is a really long way of saying you don't fuck.", "Sorry ma'am, looks like his delusions have gotten worse. We'll have to admit him.", 'If only you could put that energy into your relationships', 'Posts like this is why I do Heroine.', 'still unemployed then?', 'K', 'look im gunna have 2 ask u 2 keep ur giant dumps in the toilet not in my replys 😷😷😷', "Mommy is soooo proud of you, sweaty. Let's put this sperg out up on the fridge with all your other failures.", "Good job bobby, here's a star", "That was a mistake. You're about to find out the hard way why.", f'You sat down and wrote all this shit. You could have done so many other things with your life. What happened to your life that made you decide writing novels of bullshit here was the best option?', "I don't have enough spoons to read this shit", "All those words won't bring daddy back.", 'OUT!', "Damn, you're really mad over this, but thanks for the effort you put into typing that all out! Sadly I won't read it all.", "Jesse what the fuck are you talking about??", "▼you're fucking bananas if you think I'm reading all that, take my downvote and shut up idiot", "Are you feeling okay bud?", '<img loading="lazy" data-bs-toggle="tooltip" alt=":#marseywoah:" src="/e/marseywoah.webp" b title=":#marseywoah:">', 'At no point in your rambling, incoherent post were you even close to anything that could be considered a rational thought. Everyone on this site is now dumber for having read it. May God have mercy on your soul.')


AGENDAPOSTER_PHRASE = 'trans lives matter'


AGENDAPOSTER_MSG = """Hi @{username},\nYour {type} has been automatically removed because you forgot to include `{AGENDAPOSTER_PHRASE}`.\nDon't worry, we're here to help! We won't let you post or comment anything that doesn't express your love and acceptance towards the trans community. Feel free to resubmit your {type} with `{AGENDAPOSTER_PHRASE}` included. \n*This is an automated message; if you need help, you can message us [here](/contact).*"""

AGENDAPOSTER_MSG_HTML = """<p>Hi <a href="/id/{id}"><img loading="lazy" src="/pp/{id}">@{username}</a>,</p>
<p>Your comment has been automatically removed because you forgot to include <code>{AGENDAPOSTER_PHRASE}</code>.</p>
<p>Don't worry, we're here to help! We won't let you post or comment anything that doesn't express your love and acceptance towards the trans community. Feel free to resubmit your {type} with <code>{AGENDAPOSTER_PHRASE}</code> included.</p>
<p><em>This is an automated message; if you need help, you can message us <a href="/contact">here</a>.</em></p>"""

DISCORD_CHANGELOG_CHANNEL_ID = 1034632681788538980
WPD_CHANNEL_ID = 1013990963846332456
PIN_AWARD_TEXT = " (pin award)"

THEMES = ["4chan","classic","classic_dark","coffee","dark","dramblr","light","midnight","transparent","tron","win98"]
COMMENT_SORTS = ["hot", "new", "old", "top", "bottom", "controversial"]
SORTS = COMMENT_SORTS + ["bump", "comments"]
TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"]
PAGE_SIZES = {10, 25, 50, 100}

################################################################################
### SITE SPECIFIC CONSTANTS
################################################################################

PERMS = { # Minimum admin_level to perform action.
	'ADMIN_ADD': 3,
	'ADMIN_REMOVE': 3,
	'ADMIN_ADD_PERM_LEVEL': 2, # permission level given when user added via site
	'ADMIN_ACTIONS_REVERT': 3,
	'ADMIN_MOP_VISIBLE': 2,
	'ADMIN_HOME_VISIBLE': 2,
	'CHAT_BYPASS_MUTE': 2,
	'DOMAINS_BAN': 3,
	'HOLE_CREATE': 0,
	'FLAGS_REMOVE': 2,
	'VOTES_VISIBLE': 0,
	'USER_BLOCKS_VISIBLE': 0,
	'USER_FOLLOWS_VISIBLE': 0,
	'USER_VOTERS_VISIBLE': 0,
	'POST_COMMENT_INFINITE_PINGS': 1,
	'POST_COMMENT_MODERATION': 2,
	'POST_COMMENT_DISTINGUISH': 1,
	'POST_COMMENT_MODERATION_TOOLS_VISIBLE': 2, # note: does not affect API at all
	'POST_BYPASS_REPOST_CHECKING': 1,
	'POST_EDITING': 3,
	'USER_BADGES': 2,
	'USER_BAN': 2,
	'USER_SHADOWBAN': 2,
	'USER_AGENDAPOSTER': 2,
	'USER_CLUB_ALLOW_BAN': 2,
	'USER_LINK': 2,
	'USER_MERGE': 3, # note: extra check for Aevann
	'USER_TITLE_CHANGE': 2,
	'USER_MODERATION_TOOLS_VISIBLE': 2, # note: does not affect API at all
	'POST_IN_GHOST_THREADS': 1,
	'POST_TO_CHANGELOG': 1, # note: code contributors can also post to changelog
	'POST_TO_POLL_THREAD': 2,
	'POST_BETS': 3,
	'POST_BETS_DISTRIBUTE': 3, # probably should be the same as POST_BETS but w/e
	'VIEW_PENDING_SUBMITTED_MARSEYS': 3,
	'VIEW_PENDING_SUBMITTED_HATS': 3,
	'MODERATE_PENDING_SUBMITTED_MARSEYS': 3, # note: there is an extra check so that only """carp""" can approve them
	'MODERATE_PENDING_SUBMITTED_HATS': 3, # note: there is an extra check so that only """carp""" can approve them
	'UPDATE_MARSEYS': 3, # note: extra check is here for 4 different users
	'UPDATE_HATS': 3, # note: extra check is here for 4 different users
	'BUY_GHOST_AWARD': 2,
	'LOTTERY_ADMIN': 3,
	'LOTTERY_VIEW_PARTICIPANTS': 2,
	'VIEW_MODMAIL': 2,
	'VIEW_CLUB': 1,
	'VIEW_CHUDRAMA': 1,
	'VIEW_PRIVATE_PROFILES': 2,
	'VIEW_ALTS': 2,
	'VIEW_PROFILE_VIEWS': 2,
	'VIEW_SORTED_ADMIN_LIST': 3,
	'VIEW_ACTIVE_USERS': 2,
	'VIEW_ALL_USERS': 2,
	'VIEW_ALT_VOTES': 2,
	'VIEW_LAST_ACTIVE': 2,
	'VIEW_PATRONS': 3, # note: extra check for Aevann, carp, or snakes
	'VIEW_VOTE_BUTTONS_ON_USER_PAGE': 2,
	'PRINT_MARSEYBUX_FOR_KIPPY_ON_PCMEMES': 3, # note: explicitly disabled on rDrama
	'SITE_BYPASS_READ_ONLY_MODE': 1,
	'SITE_SETTINGS': 3,
	'SITE_SETTINGS_SIDEBARS_BANNERS_BADGES': 3,
	'SITE_SETTINGS_SNAPPY_QUOTES': 3,
	'SITE_SETTINGS_UNDER_ATTACK': 3,
	'SITE_CACHE_PURGE_CDN': 3,
	'SITE_CACHE_DUMP_INTERNAL': 2,
	'SITE_WARN_ON_INVALID_AUTH': 1,
	'NOTIFICATIONS_ADMIN_PING': 2,
	'NOTIFICATIONS_HOLE_INACTIVITY_DELETION': 2,
	'NOTIFICATIONS_HOLE_CREATION': 2,
	'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 3,
	'NOTIFICATIONS_MODMAIL': 3,
	'NOTIFICATIONS_MODERATOR_ACTIONS': 2,
	'NOTIFICATIONS_REDDIT': 1,
	'NOTIFICATIONS_SPECIFIC_WPD_COMMENTS': 1,
	'MESSAGE_BLOCKED_USERS': 1,
	'APPS_MODERATION': 3,
	'STREAMERS_MODERATION': 2,
}

FEATURES = {
	'PROCOINS': True,
	'AWARDS': True,
	'CHAT': True,
	'PINS': True,
	'COUNTRY_CLUB': True,
	'PRONOUNS': False,
	'BADGES': True,
	'HATS': True,
	'HOUSES': False,
	'GAMBLING': True,
	'WORDLE': True,
	'USERS_PROFILE_BANNER': True,
	'USERS_PROFILE_BODYTEXT': True,
	'USERS_PROFILE_SONG': True,
	'USERS_PERMANENT_WORD_FILTERS': False,
	'USERS_SUICIDE': True,
	'MARKUP_COMMANDS': True,
	'REPOST_DETECTION': True,
	'PATRON_ICONS': False,
	'ASSET_SUBMISSIONS': False,
	'STREAMERS': False,
}

WERKZEUG_ERROR_DESCRIPTIONS = {
	400: "The browser (or proxy) sent a request that this server could not understand.",
	401: "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.",
	403: "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.",
	404: "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
	405: "The method is not allowed for the requested URL.",
	406: "The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
	409: "A conflict happened while processing the request. The resource might have been modified while the request was being processed.",
	410: "The requested URL is no longer available on this server and there is no forwarding address. If you followed a link from a foreign page, please contact the author of this page.",
	413: "The data value transmitted exceeds the capacity limit.",
	414: "The length of the requested URL exceeds the capacity limit for this server. The request cannot be processed.",
	415: "The server does not support the media type transmitted in the request.",
	417: "The server could not meet the requirements of the Expect header",
	418: "This server is a teapot, not a coffee machine",
	429: "This user has exceeded an allotted request count. Try again later.",
	500: "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.",
}

ERROR_TITLES = {
	400: "Naughty Request",
	401: "🚫 Unauthorized 🚫",
	403: "Forbidden🙅‍♀️",
	404: "Not Found - where did it go?",
	405: "Method Not Allowed, BAD.",
	406: "Too Many Pings fuck off",
	409: "Cumflict",
	410: "Gone... and Forgotten",
	413: "Gayload Too Large",
	415: "Weird Media Type",
	418: "I'm a teapot",
	429: "Too Many Requests",
	500: "Balls-Deep Server Error",
}

ERROR_MSGS = {
	400: "That request was bad and you should feel bad.",
	401: "What you're trying to do requires an account. I think. The original error message said something about a castle and I hated that. If you see this error and you're logged into an account, something went pretty wrong somewhere.",
	403: "YOU AREN'T WELCOME HERE GO AWAY",
	404: "Someone typed something wrong and it was probably you, please do better.",
	405: "idk how anyone gets this error but if you see this, remember to follow @carpathianflorist<br>the original error text here talked about internet gremlins and wtf",
	406: "Max limit is 5 for comments and 50 for posts (what is it referring to? what does it mean? no one knows)",
	409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do. So maybe like... don't try and do that? Sorry not sorry",
	410: "You were too slow. The link FUCKING DIED. Request a new one and be more efficient.",
	413: "That's a heckin' chonker of a file! Please make it smaller or maybe like upload it somewhere else idk<BR>jc wrote this one hi jc!<br>- carp",
	415: "Please upload only Image, Video, or Audio files!",
	418: "this really shouldn't happen now that we autoconvert webm files but if it does there's a cool teapot marsey so there's that",
	429: "go spam somewhere else nerd",
	500: "Hiiiii it's carp! I think this error means that there's a timeout error. And I think that means something took too long to load so it decided not to work at all. If you keep seeing this on the same page <I>but not other pages</I>, then something is probably wrong with that specific function. It may not be called a function, but that sounds right to me. Anyway, <s>ping me and I'll whine to someone smarter to fix it. Don't bother them.</s> <B>After a year and a half of infuriating pings, the new instructions are to quit whining and just wait until it works again oh my god shut UP.</B><BR><BR> Thanks ily &lt;3",
}

ERROR_MARSEYS = {
	400: "marseybrainlet",
	401: "marseydead",
	403: "marseytroll",
	404: "marseyconfused",
	405: "marseyretard",
	406: "marseyrage",
	409: "marseynoyou",
	410: "marseyrave",
	413: "marseychonker2",
	415: "marseydetective",
	418: "marseytea",
	429: "marseyrentfree",
	500: "marseycarp3",
}

EMOJI_MARSEYS = True
EMOJI_SRCS = ['files/assets/emojis.json']

PIN_LIMIT = 3
POST_RATE_LIMIT = '1/second;10/hour;50/day'
POST_TITLE_LENGTH_LIMIT = 500 # do not make larger than 500 without altering the table
POST_TITLE_HTML_LENGTH_LIMIT = 1500 # do not make larger than 1500 without altering the table
POST_BODY_LENGTH_LIMIT = 20000 # do not make larger than 20000 without altering the table
POST_BODY_HTML_LENGTH_LIMIT = 40000 # do not make larger than 40000 without altering the table
COMMENT_BODY_LENGTH_LIMIT = 10000 # do not make larger than 10000 characters without altering the table
COMMENT_BODY_HTML_LENGTH_LIMIT = 20000 # do not make larger than 20000 characters without altering the table
COMMENT_MAX_DEPTH = 200
TRANSFER_MESSAGE_LENGTH_LIMIT = 200 # do not make larger than 10000 characters (comment limit) without altering the table
MIN_REPOST_CHECK_URL_LENGTH = 9 # also change the constant in checkRepost() of submit.js
CHAT_LENGTH_LIMIT = 1000
TRUESCORE_DONATE_LIMIT = 100
COSMETIC_AWARD_COIN_AWARD_PCT = 0.10
TRUESCORE_CHAT_LIMIT = 0
TRUESCORE_GHOST_LIMIT = 0

LOGGEDIN_ACTIVE_TIME = 15 * 60
PFP_DEFAULT_MARSEY = True
NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400
COMMENT_SPAM_LENGTH_THRESHOLD = 50

HOLE_NAME = 'hole'
HOLE_STYLE_FLAIR = False
HOLE_REQUIRED = False
HOLE_COST = 0
HOLE_INACTIVITY_DELETION = False

AUTOJANNY_ID = 1
SNAPPY_ID = 2
LONGPOSTBOT_ID = 3
ZOZBOT_ID = 4
BASEDBOT_ID = 0
PRIVILEGED_USER_BOTS = ()

SCHIZO_ID = 0
KIPPY_ID = 0
MCCOX_ID = 0
CHIOBU_ID = 0
PIZZASHILL_ID = 0
IMPASSIONATA_ID = 0
GUMROAD_MESSY = ()
IDIO_ID = 0
CARP_ID = 0
JOAN_ID = 0
AEVANN_ID = 0
SNAKES_ID = 0
JUSTCOOL_ID = 0
HOMO_ID = 0
SOREN_ID = 0
LAWLZ_ID = 0
DAD_ID = 0
MOM_ID = 0
DONGER_ID = 0
GEESE_ID = 0
BLACKJACKBTZ_ID = 0
MODMAIL_ID = 2

POLL_THREAD = 0
POLL_BET_COINS = 200
WELCOME_MSG = f"Welcome to {SITE_NAME}!"

LOTTERY_TICKET_COST = 12
LOTTERY_SINK_RATE = 3
LOTTERY_DURATION = 60 * 60 * 24 * 7

SIDEBAR_THREAD = 0
BANNER_THREAD = 0
BADGE_THREAD = 0
SNAPPY_THREAD = 0
GIFT_NOTIF_ID = 5
SIGNUP_FOLLOW_ID = 0
NOTIFICATION_THREAD = 1

MAX_IMAGE_SIZE_BANNER_RESIZED_KB = 500
MAX_IMAGE_AUDIO_SIZE_MB = 8
MAX_IMAGE_AUDIO_SIZE_MB_PATRON = 16
MAX_VIDEO_SIZE_MB = 32
MAX_VIDEO_SIZE_MB_PATRON = 64
MAX_IMAGE_CONVERSION_TIMEOUT = 15 # seconds

ANTISPAM_BYPASS_IDS = ()

PAGE_SIZE = 25
LEADERBOARD_LIMIT = PAGE_SIZE

HOUSE_JOIN_COST = 500
HOUSE_SWITCH_COST = 2000

DONATE_SERVICE = "Gumroad" if not KOFI_TOKEN or  KOFI_TOKEN == DEFAULT_CONFIG_VALUE else "KoFi"
DONATE_LINK = GUMROAD_LINK if not KOFI_TOKEN or KOFI_TOKEN == DEFAULT_CONFIG_VALUE else KOFI_LINK

TIERS_ID_TO_NAME = {
		1: "Paypig",
		2: "Renthog",
		3: "Landchad",
		4: "Terminally online turboautist",
		5: "JIDF Bankroller",
		6: "Rich Bich"
}

if SITE == 'rdrama.net':
	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	FEATURES['ASSET_SUBMISSIONS'] = True
	PERMS['ADMIN_ADD'] = 4

	SIDEBAR_THREAD = 37696
	BANNER_THREAD = 37697
	BADGE_THREAD = 37833
	SNAPPY_THREAD = 37749
	NOTIFICATION_THREAD = 6489

	CHAT_LENGTH_LIMIT = 200

	TRUESCORE_CHAT_LIMIT = 10
	TRUESCORE_GHOST_LIMIT = 10

	HOLE_COST = 50000
	HOLE_INACTIVITY_DELETION = True

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833
	PRIVILEGED_USER_BOTS = (12125, 16049)

	SCHIZO_ID = 8494
	KIPPY_ID = 7150
	MCCOX_ID = 8239
	CHIOBU_ID = 5214
	PIZZASHILL_ID = 2424
	IMPASSIONATA_ID = 5800
	GUMROAD_MESSY = (1230,1379)
	IDIO_ID = 30
	CARP_ID = 995
	JOAN_ID = 28
	AEVANN_ID = 1
	SNAKES_ID = 10288
	JUSTCOOL_ID = 4999
	HOMO_ID = 147
	SOREN_ID = 2546
	LAWLZ_ID = 3833
	DAD_ID = 2513
	MOM_ID = 4588
	DONGER_ID = 541
	GEESE_ID = 1710
	BLACKJACKBTZ_ID = 12732

	ANTISPAM_BYPASS_IDS = (1703, 13427)

	GIFT_NOTIF_ID = CARP_ID

	POLL_THREAD = 79285

	WELCOME_MSG = "Hi there! It's me, your soon-to-be favorite rDrama user @carpathianflorist here to give you a brief rundown on some of the sick features we have here. You'll probably want to start by following me, though. So go ahead and click my name and then smash that Follow button. This is actually really important, so go on. Hurry.\n\nThanks!\n\nNext up: If you're a member of the media, similarly just shoot me a DM and I'll set about verifying you and then we can take care of your sad journalism stuff.\n\n**FOR EVERYONE ELSE**\n\n Begin by navigating to [the settings page](/settings/profile) (we'll be prettying this up so it's less convoluted soon, don't worry) and getting some basic customization done.\n\n### Themes\n\nDefinitely change your theme right away, the default one (Midnight) is pretty enough, but why not use something *exotic* like Win98, or *flashy* like Tron? Even Coffee is super tasteful and way more fun than the default. More themes to come when we get around to it!\n\n### Avatar/pfp\n\nYou'll want to set this pretty soon. Set the banner too while you're at it. Your profile is important!\n\n### Flairs\n\nSince you're already on the settings page, you may as well set a flair, too. As with your username, you can - obviously - choose the color of this, either with a hex value or just from the preset colors. And also like your username, you can change this at any time. Paypigs can even further relive the glory days of 90s-00s internet and set obnoxious signatures.\n\n### PROFILE ANTHEMS\n\nSpeaking of profiles, hey, remember MySpace? Do you miss autoplaying music assaulting your ears every time you visited a friend's page? Yeah, we brought that back. Enter a YouTube URL, wait a few seconds for it to process, and then BAM! you've got a profile anthem which people cannot mute. Unless they spend 20,000 dramacoin in the shop for a mute button. Which you can then remove from your profile by spending 40,000 dramacoin on an unmuteable anthem. Get fucked poors!\n\n### Dramacoin?\n\nDramacoin is basically our take on the karma system. Except unlike the karma system, it's not gay and boring and stupid and useless. Dramacoin can be spent at [Marsey's Dramacoin Emporium](/shop) on upgrades to your user experience (many more coming than what's already listed there), and best of all on tremendously annoying awards to fuck with your fellow dramautists. We're always adding more, so check back regularly in case you happen to miss one of the announcement posts.\n\nLike karma, dramacoin is obtained by getting upvotes on your threads and comments. *Unlike* karma, it's also obtained by getting downvotes on your threads and comments. Downvotes don't really do anything here - they pay the same amount of dramacoin and they increase thread/comment ranking just the same as an upvote. You just use them to express petty disapproval and hopefully start a fight. Because all votes are visible here. To hell with your anonymity.\n\nDramacoin can also be traded amongst users from their profiles. Note that there is a 3% transaction fee.\n\n### Badges\n\nRemember all those neat little metallic icons you saw on my profile when you were following me? If not, scroll back up and go have a look. And doublecheck to make sure you pressed the Follow button. Anyway, those are badges. You earn them by doing a variety of things. Some of them even offer benefits, like discounts at the shop. A [complete list of badges and their requirements can be found here](/badges), though I add more pretty regularly, so keep an eye on the [changelog](/h/changelog).\n\n### Other stuff\n\nWe're always adding new features, and we take a fun-first approach to development. If you have a suggestion for something that would be fun, funny, annoying - or best of all, some combination of all three - definitely make a thread about it. Or just DM me if you're shy. Weirdo. Anyway there's also the [leaderboards](/leaderboard), boring stuff like two-factor authentication you can toggle on somewhere in the settings page (psycho), the ability to save posts and comments, more than a thousand emojis already (most of which are rDrama originals), and on and on and on and on. This is just the basics, mostly to help you get acquainted with some of the things you can do here to make it more easy on the eyes, customizable, and enjoyable. If you don't enjoy it, just go away! We're not changing things to suit you! Get out of here loser! And no, you can't delete your account :na:\n\nI love you.<br>*xoxo Carp* 💋"
elif SITE == 'pcmemes.net':
	PIN_LIMIT = 10
	FEATURES['REPOST_DETECTION'] = False
	FEATURES['STREAMERS'] = True
	ERROR_MSGS[500] = "Hiiiii it's <b>nigger</b>! I think this error means that there's a <b>nigger</b> error. And I think that means something took too long to load so it decided to be a <b>nigger</b>. If you keep seeing this on the same page but not other pages, then something its probably a <b>niggerfaggot</b>. It may not be called a <b>nigger</b>, but that sounds right to me. Anyway, ping me and I'll whine to someone smarter to fix it. Don't bother them. Thanks ily &lt;3"
	ERROR_MARSEYS[500] = "wholesome"
	POST_RATE_LIMIT = '1/second;4/minute;20/hour;100/day'

	HOLE_COST = 2000

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833
	BASEDBOT_ID = 800

	KIPPY_ID = 1592
	GIFT_NOTIF_ID = KIPPY_ID
	SIGNUP_FOLLOW_ID = KIPPY_ID
	NOTIFICATION_THREAD = 2487
	CARP_ID = 13
	AEVANN_ID = 1
	SNAKES_ID = 2279

	WELCOME_MSG = "Welcome to pcmemes.net! Don't forget to turn off the slur filter [here](/settings/content#slurreplacer)!"

	LOTTERY_TICKET_COST = 12
	LOTTERY_SINK_RATE = -8

	BANNER_THREAD = 28307
elif SITE == 'watchpeopledie.tv':
	PIN_LIMIT = 4
	WELCOME_MSG = """Hi, you! Welcome to WatchPeopleDie.tv, this really cool site where you can go to watch people die. I'm @CLiTPEELER! If you have any questions about how things work here, or suggestions on how to make them work better than they already do, definitely slide on into my DMs (no fat chicks).\nThere's an enormously robust suite of fun features we have here and we're always looking for more to add. Way, way too many to go over in an automated welcome message. And you're probably here for the videos of people dying more than any sort of weird, paradoxical digital community aspect anyway, so I won't bore you with a tedious overview of them. Just head on over to [your settings page](https://watchpeopledie.tv/settings/profile) and have a look at some of the basic profile stuff, at least. You can change your profile picture, username, flair, colors, banners, bio, profile anthem (autoplaying song on your page, like it's MySpace or some shit, hell yeah), CSS, all sorts of things.\nOr you can just go back to the main feed and carry on with watching people die. That's what the site is for, after all. Have fun!\nAnyway, in closing, WPD is entirely open source. We don't really need new full-time coders or anything, but if you'd like to take a look at our repo - or even submit a PR to change, fix, or add some things - go right ahead! We are on [GitHub](https://github.com/Aevann1/rDrama).\nWell, that's all. Thanks again for signing up. It's an automated message and all, but I really do mean that. Thank you, specifically. I love you. Romantically. Deeply. Passionately.\nHave fun!"""

	FEATURES['PATRON_ICONS'] = True

	PERMS['HOLE_CREATE'] = 2
	PERMS['POST_EDITING'] = 2
	PERMS['ADMIN_ADD'] = 4
	
	ERROR_TITLES[400] = "Bad Request"
	ERROR_TITLES[401] = "Unauthorized"
	ERROR_TITLES[403] = "Forbidden"
	ERROR_TITLES[404] = "Not Found"
	ERROR_TITLES[405] = "Method Not Allowed"
	ERROR_TITLES[406] = "Too Many Pings"
	ERROR_TITLES[409] = "Mortal Conflict"
	ERROR_TITLES[410] = "Dead"
	ERROR_TITLES[413] = "Payload Too Large"
	ERROR_TITLES[415] = "Unsupported Media Type"
	ERROR_TITLES[500] = "Internal Server Error"
	ERROR_MSGS[400] = "That request is invalid"
	ERROR_MSGS[401] = "You need to login or sign up to do that"
	ERROR_MSGS[403] = "You're not allowed to do that"
	ERROR_MSGS[404] = "That wasn't found"
	ERROR_MSGS[405] = "You can't use this method here... if you keep getting this error tell us it's prolly something borked"
	ERROR_MSGS[409] = "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do."
	ERROR_MSGS[410] = "This link is dead. Request a new one to try again"
	ERROR_MSGS[413] = "You need to upload a smaller file please"
	ERROR_MSGS[429] = "Please wait a bit before doing that"

	POLL_THREAD = 13225

	SIDEBAR_THREAD = 5403
	BANNER_THREAD = 9869

	TRUESCORE_CHAT_LIMIT = 10
	TRUESCORE_GHOST_LIMIT = 10

	HOLE_NAME = 'flair'
	HOLE_STYLE_FLAIR = True
	HOLE_REQUIRED = True

	AUTOJANNY_ID = 1
	SNAPPY_ID = 3
	LONGPOSTBOT_ID = 4
	ZOZBOT_ID = 5

	CARP_ID = 14668
	AEVANN_ID = 9
	SNAKES_ID = 32

	GIFT_NOTIF_ID = CARP_ID
	SIGNUP_FOLLOW_ID = CARP_ID

	TIERS_ID_TO_NAME = {
		1: "Victim",
		2: "Corpse",
		3: "Zombie",
		4: "Ghost",
		5: "Survivor",
		6: "Jigsaw"
	}

else: # localhost or testing environment implied
	FEATURES['ASSET_SUBMISSIONS'] = True
	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	FEATURES['STREAMERS'] = True

HOUSES = ("None","Furry","Femboy","Vampire","Racist") if FEATURES['HOUSES'] else ("None")

bots = {AUTOJANNY_ID, SNAPPY_ID, LONGPOSTBOT_ID, ZOZBOT_ID, BASEDBOT_ID}

COLORS = {'ff66ac','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58','8cdbe6', DEFAULT_COLOR}

BAN_EVASION_DOMAIN = 'rdrama.life'

AWARDS = {
	### Deprecated
	"ghost": {
		"kind": "ghost",
		"title": "Ghost",
		"description": "",
		"icon": "fas fa-ghost",
		"color": "text-white",
		"price": 3000,
		"deflectable": False,
		"cosmetic": False
	},
	"nword": {
		"kind": "nword",
		"title": "Nword Pass",
		"description": "",
		"icon": "fas fa-edit",
		"color": "text-success",
		"price": 10000,
		"deflectable": True,
		"cosmetic": False
	},
	### Fistmas 2021
	"snow": {
		"kind": "snow",
		"title": "Snow",
		"description": "",
		"icon": "fas fa-snowflake",
		"color": "text-blue-200",
		"price": 300,
		"deflectable": False,
		"cosmetic": True
	},
	"gingerbread": {
		"kind": "gingerbread",
		"title": "Gingerbread",
		"description": "",
		"icon": "fas fa-gingerbread-man",
		"color": "",
		"price": 300,
		"deflectable": False,
		"cosmetic": True
	},
	"lights": {
		"kind": "lights",
		"title": "Lights",
		"description": "",
		"icon": "fas fa-lights-holiday",
		"color": "",
		"price": 300,
		"deflectable": False,
		"cosmetic": True
	},
	"candycane": {
		"kind": "candycane",
		"title": "Candy Cane",
		"description": "",
		"icon": "fas fa-candy-cane",
		"color": "",
		"price": 400,
		"deflectable": False,
		"cosmetic": True
	},
	"fireplace": {
		"kind": "fireplace",
		"title": "Fireplace",
		"description": "",
		"icon": "fas fa-fireplace",
		"color": "",
		"price": 600,
		"deflectable": False,
		"cosmetic": True
	},
	"grinch": {
		"kind": "grinch",
		"title": "Grinch",
		"description": "",
		"icon": "fas fa-angry",
		"color": "text-green-500",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	### Homoween 2021 & 2022
	"haunt": {
		"kind": "haunt",
		"title": "Haunt",
		"description": "",
		"icon": "fas fa-book-dead",
		"color": "text-warning",
		"price": 500,
		"deflectable": False,
		"cosmetic": True
	},
	"upsidedown": {
		"kind": "upsidedown",
		"title": "The Upside Down",
		"description": "",
		"icon": "fas fa-lights-holiday",
		"color": "",
		"price": 400,
		"deflectable": False,
		"cosmetic": True
	},
	"stab": {
		"kind": "stab",
		"title": "Stab",
		"description": "",
		"icon": "fas fa-knife-kitchen",
		"color": "text-danger",
		"price": 300,
		"deflectable": False,
		"cosmetic": True
	},
	"spiders": {
		"kind": "spiders",
		"title": "Spiders",
		"description": "",
		"icon": "fas fa-spider",
		"color": "text-black",
		"price": 200,
		"deflectable": False,
		"cosmetic": True
	},
	"fog": {
		"kind": "fog",
		"title": "Fog",
		"description": "",
		"icon": "fas fa-smoke",
		"color": "text-gray",
		"price": 200,
		"deflectable": False,
		"cosmetic": True
	},
	### Homoween 2022
	"jumpscare": {
		"kind": "jumpscare",
		"title": "Jumpscare",
		"description": "",
		"icon": "fas fa-coffin-cross",
		"color": "text-purple",
		"price": 600,
		"deflectable": True,
		"cosmetic": False
	},
	"hw-bite": {
		"kind": "hw-bite",
		"title": "Zombie Bite",
		"description": "",
		"icon": "fas fa-biohazard",
		"color": "text-danger",
		"price": 500,
		"deflectable": True,
		"cosmetic": False
	},
	"hw-vax": {
		"kind": "hw-vax",
		"title": "Vaxxmaxx",
		"description": "",
		"icon": "fas fa-syringe",
		"color": "text-blue",
		"price": 500,
		"deflectable": True,
		"cosmetic": False
	},
	"hw-grinch": {
		"kind": "hw-grinch",
		"title": "Hallowgrinch",
		"description": "",
		"icon": "fas fa-angry",
		"color": "text-orange",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	"flashlight": {
		"kind": "flashlight",
		"title": "Flashlight",
		"description": "",
		"icon": "fas fa-flashlight",
		"color": "text-black",
		"price": 400,
		"deflectable": False,
		"cosmetic": True
	},
	"candy-corn": {
		"kind": "candy-corn",
		"title": "Candy Corn",
		"description": "",
		"icon": "fas fa-candy-corn",
		"color": "text-orange",
		"price": 400,
		"deflectable": False,
		"cosmetic": True
	},
	"ectoplasm": {
		"kind": "ectoplasm",
		"title": "Ectoplasm",
		"description": "",
		"icon": "fas fa-ghost",
		"color": "text-success",
		"price": 400,
		"deflectable": False,
		"cosmetic": True
	},
	"bones": {
		"kind": "bones",
		"title": "Bones",
		"description": "",
		"icon": "fas fa-bone",
		"color": "text-white",
		"price": 200,
		"deflectable": False,
		"cosmetic": True
	},
	"pumpkin": {
		"kind": "pumpkin",
		"title": "Pumpkin",
		"description": "",
		"icon": "fas fa-jack-o-lantern",
		"color": "text-orange",
		"price": 200,
		"deflectable": False,
		"cosmetic": True
	},
	### Standard
	"marsify": {
		"kind": "marsify",
		"title": "Marsify",
		"description": "Marsifies the recipient's comments for 24 hours.",
		"icon": "fas fa-cat",
		"color": "text-white",
		"price": 150,
		"deflectable": True,
		"cosmetic": False
	},
	"shit": {
		"kind": "shit",
		"title": "Shit",
		"description": "Makes flies swarm the post.",
		"icon": "fas fa-poop",
		"color": "text-black-50",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"fireflies": {
		"kind": "fireflies",
		"title": "Fireflies",
		"description": "Makes fireflies swarm the post.",
		"icon": "fas fa-sparkles",
		"color": "text-warning",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"train": {
		"kind": "train",
		"title": "Train",
		"description": "Summons a train on the post.",
		"icon": "fas fa-train",
		"color": "text-pink",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"scooter": {
		"kind": "scooter",
		"title": "Scooter",
		"description": "Summons a scooter on the post.",
		"icon": "fas fa-flag-usa",
		"color": "text-muted",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"wholesome": {
		"kind": "wholesome",
		"title": "Wholesome",
		"description": "Summons a wholesome marsey on the post.",
		"icon": "fas fa-smile-beam",
		"color": "text-yellow",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"firework": {
		"kind": "firework",
		"title": "Fireworks",
		"description": "Summons fireworks on the post.",
		"icon": "fas fa-bahai",
		"color": "text-danger",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"confetti": {
		"kind": "confetti",
		"title": "Confetti",
		"description": "Summons confetti to fall on the post.",
		"icon": "fas fa-party-horn",
		"color": "text-yellow",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"ricardo": {
		"kind": "ricardo",
		"title": "Stripper Cake",
		"description": "Summons Ricardo to dance on the post.",
		"icon": "fas fa-pinata",
		"color": "text-pink",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"tilt": {
		"kind": "tilt",
		"title": "Tilt",
		"description": "Tilts the post or comment",
		"icon": "fas fa-car-tilt",
		"color": "text-blue",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"glowie": {
		"kind": "glowie",
		"title": "Glowie",
		"description": "Indicates that the recipient can be seen when driving. Just run them over.",
		"icon": "fas fa-user-secret",
		"color": "text-green",
		"price": 150,
		"deflectable": False,
		"cosmetic": True
	},
	"rehab": {
		"kind": "rehab",
		"title": "Rehab",
		"description": "Prevents the user from gambling for 24 hours in a last ditch effort to save them from themself.",
		"icon": "fas fa-dice-six",
		"color": "text-black",
		"price": 777,
		"deflectable": True,
		"cosmetic": False
	},
	"agendaposter": {
		"kind": "agendaposter",
		"title": "Chud",
		"description": "Chuds the recipient for 24 hours.",
		"icon": "fas fa-snooze",
		"color": "text-purple",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	"offsitementions": {
		"kind": "offsitementions",
		"title": "Y'all Seein' Eye",
		"description": "Gives the recipient access to notifications when people off-site talk about us.",
		"icon": "fas fa-eyes",
		"color": "text-orange",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	"lootbox": {
		"kind": "lootbox",
		"title": "Lootbox",
		"description": "",
		"icon": "fas fa-box-open",
		"color": "text-blue",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	"beano": {
		"kind": "beano",
		"title": "Beano",
		"description": "Stops you from embarrassing yourself with your flatulence",
		"icon": "fas fa-gas-pump-slash",
		"color": "text-green",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False
	},
	"unpin": {
		"kind": "unpin",
		"title": "Unpin",
		"description": "Removes 1 hour from the pin duration of a post or 6 hours from the pin duration of a comment.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-black",
		"price": 1000,
		"deflectable": False,
		"cosmetic": False
	},
	"flairlock": {
		"kind": "flairlock",
		"title": "1-Day Flairlock",
		"description": "Sets a flair for the recipient and locks it for 24 hours.",
		"icon": "fas fa-lock",
		"color": "text-black",
		"price": 1250,
		"deflectable": True,
		"cosmetic": False
	},
	"pin": {
		"kind": "pin",
		"title": "Pin",
		"description": "Pins a post for 1 hour or a comment for 6 hours.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-warning",
		"price": 1500,
		"deflectable": False,
		"cosmetic": False
	},
	"progressivestack": {
		"kind": "progressivestack",
		"title": "Progressive Stack",
		"description": "Makes votes on the recipient's posts and comments weigh double in the ranking algorithm for 6 hours.",
		"icon": "fas fa-bullhorn",
		"color": "text-danger",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False
	},
	"pizzashill": {
		"kind": "pizzashill",
		"title": "Pizzashill",
		"description": "Forces the recipient to make all posts/comments > 280 characters for 24 hours.",
		"icon": "fas fa-pizza-slice",
		"color": "text-orange",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False
	},
	"bird": {
		"kind": "bird",
		"title": "Bird Site",
		"description": "Forces the recipient to make all posts/comments < 140 characters for 24 hours.",
		"icon": "fab fa-twitter",
		"color": "text-blue",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False
	},
	"spider": {
		"kind": "spider",
		"title": "Spider!",
		"description": f"Summons a spider to terrorize the recipient for 24 hours.",
		"icon": "fas fa-spider",
		"color": "text-brown",
		"price": 2000,
		"deflectable": True,
		"cosmetic": False
	},
	"deflector": {
		"kind": "deflector",
		"title": "Deflector",
		"description": "Causes most awards received for the next 10 hours to be deflected back at their giver.",
		"icon": "fas fa-shield",
		"color": "text-pink",
		"price": 2750,
		"deflectable": True,
		"cosmetic": False
	},
	"marsey": {
		"kind": "marsey",
		"title": "Marsey",
		"description": "Makes the recipient unable to post/comment anything but marsey emojis for 24 hours.",
		"icon": "fas fa-cat",
		"color": "text-orange",
		"price": 3000,
		"deflectable": True,
		"cosmetic": False
	},
	"ban": {
		"kind": "ban",
		"title": "1-Day Ban",
		"description": "Bans the recipient for a day.",
		"icon": "fas fa-gavel",
		"color": "text-danger",
		"price": 3000,
		"deflectable": True,
		"cosmetic": False
	},
	"unban": {
		"kind": "unban",
		"title": "1-Day Unban",
		"description": "Removes 1 day from the ban duration of the recipient.",
		"icon": "fas fa-gavel",
		"color": "text-success",
		"price": 3500,
		"deflectable": True,
		"cosmetic": False
	},
	"benefactor": {
		"kind": "benefactor",
		"title": "Benefactor",
		"description": f"Grants one month of {patron} status and 2500 marseybux to the recipient. Cannot be used on yourself.",
		"icon": "fas fa-gift",
		"color": "text-blue",
		"price": 4000,
		"deflectable": False,
		"cosmetic": False
	},
	"grass": {
		"kind": "grass",
		"title": "Grass",
		"description": "Ban the recipient for 30 days (if they provide a timestamped picture of them touching grass/snow/sand/ass to the admins, they will get unbanned immediately)",
		"icon": "fas fa-seedling",
		"color": "text-success",
		"price": 10000,
		"deflectable": True,
		"cosmetic": False
	},
	"eye": {
		"kind": "eye",
		"title": "All-Seeing Eye",
		"description": "Gives the recipient the ability to view private profiles.",
		"icon": "fas fa-eye",
		"color": "text-silver",
		"price": 10000,
		"deflectable": True,
		"cosmetic": False
	},
	"unblockable": {
		"kind": "unblockable",
		"title": "Unblockable",
		"description": "Makes the recipient unblockable and removes all blocks on them.",
		"icon": "fas fa-laugh-squint",
		"color": "text-lightgreen",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False
	},
	"fish": {
		"kind": "fish",
		"title": "Fish",
		"description": "This user cannot be unfollowed",
		"icon": "fas fa-fish",
		"color": "text-lightblue",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False
	},
	"pause": {
		"kind": "pause",
		"title": "Pause",
		"description": "Gives the recipient the ability to pause profile anthems.",
		"icon": "fas fa-volume-mute",
		"color": "text-danger",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False
	},
	"unpausable": {
		"kind": "unpausable",
		"title": "Unpausable",
		"description": "Makes the profile anthem of the recipient unpausable.",
		"icon": "fas fa-volume",
		"color": "text-success",
		"price": 40000,
		"deflectable": True,
		"cosmetic": False
	},
	"alt": {
		"kind": "alt",
		"title": "Alt-Seeing Eye",
		"description": "Gives the recipient the ability to view alts.",
		"icon": "fas fa-eye",
		"color": "text-gold",
		"price": 50000,
		"deflectable": True,
		"cosmetic": False
	},
	"checkmark": {
		"kind": "checkmark",
		"title": "Checkmark",
		"description": "Gives the recipient a checkmark.",
		"icon": "fas fa-badge-check",
		"color": "checkmark",
		"price": 50000,
		"deflectable": True,
		"cosmetic": False
	},
}

if SITE_NAME != 'rDrama':
	EXTRA_AWARDS = {
		"owoify": {
			"kind": "owoify",
			"title": "OwOify",
			"description": "OwOifies the recipient's comments for 6 hours.",
			"icon": "fas fa-paw-simple",
			"color": "text-purple",
			"price": 400,
			"deflectable": True,
			"cosmetic": False
		},
		"rainbow": {
			"kind": "rainbow",
			"title": "Rainbow",
			"description": "Makes the recipient's comments and posts in rainbow text for 24 hours.",
			"icon": "fas fa-cloud-rainbow",
			"color": "text-pink",
			"price": 400,
			"deflectable": True,
			"cosmetic": False
		},
	}
	AWARDS.update(EXTRA_AWARDS)

if SITE_NAME == 'PCM':
	PCM_AWARDS = {
		"croag": {
			"kind": "croag",
			"title": "Croag",
			"description": "Summons Croag on the post.",
			"icon": "fas fa-head-side",
			"color": "text-gold",
			"price": 150,
			"deflectable": False,
			"cosmetic": True
		},
		"toe": {
			"kind": "toe",
			"title": "Toe Hype",
			"description": "Summons Blade's toe on the post.",
			"icon": "fas fa-socks",
			"color": "text-blue",
			"price": 150,
			"deflectable": False,
			"cosmetic": True
		},
		"crab": {
			"kind": "crab",
			"title": "Crab",
			"description": "Rave time!",
			"icon": "fas fa-crab",
			"color": "text-danger",
			"price": 4000,
			"deflectable": False,
			"cosmetic": True
		}
	}
	AWARDS.update(PCM_AWARDS)

# Permit only cosmetics and pin/unpin on ghosted things.
for award in AWARDS:
	AWARDS[award]['ghost'] = AWARDS[award]['cosmetic']
AWARDS['pin']['ghost'] = True
AWARDS['unpin']['ghost'] = True

# Disable unused awards, and site-specific award inclusion/exclusion.
AWARDS_DISABLED = [
	'ghost', 'nword', 'lootbox', # Generic
	'snow', 'gingerbread', 'lights', 'candycane', 'fireplace', 'grinch', # Fistmas
	'haunt', 'upsidedown', 'stab', 'spiders', 'fog', # Homoween '21
	'jumpscare', 'hw-bite', 'hw-vax', 'hw-grinch', 'flashlight', # Homoween '22
	'candy-corn', 'ectoplasm', 'bones', 'pumpkin', # Homoween '22 (cont'd)
]


HOUSE_AWARDS = {
	"Furry": {
		"kind": "Furry",
		"title": "OwOify",
		"description": "OwOifies the recipient's comments for 6 hours.",
		"icon": "fas fa-paw-simple",
		"color": "text-purple",
		"price": 400,
		"deflectable": True,
		"cosmetic": False
	},
	"Femboy": {
		"kind": "Femboy",
		"title": "Rainbow",
		"description": "Makes the recipient's comments and posts in rainbow text for 24 hours.",
		"icon": "fas fa-cloud-rainbow",
		"color": "text-pink",
		"price": 400,
		"deflectable": True,
		"cosmetic": False
	},
	"Vampire": {
		"kind": "Vampire",
		"title": "Bite",
		"description": "Turns the recipient into a vampire for 2 days.",
		"icon": "fas fa-bat",
		"color": "text-gray",
		"price": 400,
		"deflectable": True,
		"cosmetic": False
	},
	"Racist": {
		"kind": "Racist",
		"title": "Early Life",
		"description": "Checks the recipient's Early Life section on Wikipedia. Notices.",
		"icon": "fas fa-star-of-david",
		"color": "text-yellow",
		"price": 400,
		"deflectable": True,
		"cosmetic": False
	},
}

temp = deepcopy(HOUSE_AWARDS).items()
for k, val in temp:
	HOUSE_AWARDS[f'{k} Founder'] = val
	HOUSE_AWARDS[f'{k} Founder']['kind'] += ' Founder'
	HOUSE_AWARDS[f'{k} Founder']['price'] = int(HOUSE_AWARDS[f'{k} Founder']['price'] * 0.75)

if SITE_NAME != 'rDrama':
	AWARDS_DISABLED.append('progressivestack')

if SITE_NAME == 'PCM':
	# Previous set of disabled, changed temporarily by request 2022-10-17
	#AWARDS_DISABLED.extend(['ban','pizzashill','marsey','bird','grass','chud','unblockable'])
	AWARDS_DISABLED.extend(['unblockable'])
	AWARDS_DISABLED.remove('ghost')
elif SITE_NAME == 'WPD':
	AWARDS_DISABLED.remove('lootbox')
if not FEATURES['PROCOINS']:
	AWARDS_DISABLED.append('benefactor')

AWARDS2 = {x: AWARDS[x] for x in AWARDS if x not in AWARDS_DISABLED}

DOUBLE_XP_ENABLED = -1 # set to unixtime for when DXP begins, -1 to disable

TROLLTITLES = [
	"how will @{username} ever recover?",
	"@{username} BTFO",
	"[META] Getting really sick of @{username}'s shit",
	"Pretty sure this is @{username}'s Reddit account",
	"Hey jannies can you please ban @{username}",
]

NOTIFIED_USERS = {
	'aevan': AEVANN_ID,
	'avean': AEVANN_ID,
	'joan': JOAN_ID,
	'pewkie': JOAN_ID,
	'carp': CARP_ID,
	'idio3': IDIO_ID,
	'idio ': IDIO_ID,
	'telegram ': IDIO_ID,
	'the_homocracy': HOMO_ID,
	'schizo': SCHIZO_ID,
	'snakes': SNAKES_ID,
	'sneks': SNAKES_ID,
	'snekky': SNAKES_ID,
	'jc': JUSTCOOL_ID,
	'justcool': JUSTCOOL_ID,
	'geese': GEESE_ID,
	'clit': CARP_ID,
	'kippy': KIPPY_ID,
	'mccox': MCCOX_ID,

	'lawlz': LAWLZ_ID,
	'chiobu': CHIOBU_ID,
	'donger': DONGER_ID,
	'soren': SOREN_ID,
	'pizzashill': PIZZASHILL_ID,
	'impassionata': IMPASSIONATA_ID,
}

FORTUNE_REPLIES = ('<b style="color:#6023f8">Your fortune: Allah Wills It</b>','<b style="color:#d302a7">Your fortune: Inshallah, Only Good Things Shall Come To Pass</b>','<b style="color:#e7890c">Your fortune: Allah Smiles At You This Day</b>','<b style="color:#7fec11">Your fortune: Your Bussy Is In For A Blasting</b>','<b style="color:#43fd3b">Your fortune: You Will Be Propositioned By A High-Tier Twink</b>','<b style="color:#9d05da">Your fortune: Repent, You Have Displeased Allah And His Vengeance Is Nigh</b>','<b style="color:#f51c6a">Your fortune: Reply Hazy, Try Again</b>','<b style="color:#00cbb0">Your fortune: lmao you just lost 100 coins</b>','<b style="color:#2a56fb">Your fortune: Yikes 😬</b>','<b style="color:#0893e1">Your fortune: You Will Be Blessed With Many Black Bulls</b>','<b style="color:#16f174">Your fortune: NEETmax, The Day Is Lost If You Venture Outside</b>','<b style="color:#fd4d32">Your fortune: A Taste Of Jannah Awaits You Today</b>','<b style="color:#bac200">Your fortune: Watch Your Back</b>','<b style="color:#6023f8">Your fortune: Outlook good</b>','<b style="color:#d302a7">Your fortune: Godly Luck</b>','<b style="color:#e7890c">Your fortune: Good Luck</b>','<b style="color:#7fec11">Your fortune: Bad Luck</b>','<b style="color:#43fd3b">Your fortune: Good news will come to you by mail</b>','<b style="color:#9d05da">Your fortune: Very Bad Luck</b>','<b style="color:#00cbb0">Your fortune: ｷﾀ━━━━━━(ﾟ∀ﾟ)━━━━━━ !!!!</b>','<b style="color:#2a56fb">Your fortune: Better not tell you now</b>','<b style="color:#0893e1">Your fortune: You will meet a dark handsome stranger</b>','<b style="color:#16f174">Your fortune: （　´_ゝ`）ﾌｰﾝ</b>','<b style="color:#fd4d32">Your fortune: Excellent Luck</b>','<b style="color:#bac200">Your fortune: Average Luck</b>')

FACTCHECK_REPLIES = ('<b style="color:#6023f8">Factcheck: This claim has been confirmed as correct by experts. </b>','<b style="color:#d302a7">Factcheck: This claim has been classified as misogynistic.</b>','<b style="color:#e7890c">Factcheck: This claim is currently being debunked.</b>','<b style="color:#7fec11">Factcheck: This claim is 100% true.</b>','<b style="color:#9d05da">Factcheck: This claim hurts trans lives.</b>','<b style="color:#f51c6a">Factcheck: [REDACTED].</b>','<b style="color:#00cbb0">Factcheck: This claim is both true and false.</b>','<b style="color:#2a56fb">Factcheck: You really believe that shit? Lmao dumbass nigga 🤣</b>','<b style="color:#0893e1">Factcheck: None of this is real.</b>','<b style="color:#16f174">Factcheck: Yes.</b>','<b style="color:#fd4d32">Factcheck: This claim has not been approved by experts.</b>','<b style="color:#bac200">Factcheck: This claim is a gross exageration of reality.</b>','<b style="color:#ff2200">Factcheck: WARNING! THIS CLAIM HAS BEEN CLASSIFIED AS DANGEROUS. PLEASE REMAIN STILL, AN AGENT WILL COME TO MEET YOU SHORTLY.</b>')

EIGHTBALL_REPLIES = ('<b style="color:#7FEC11">The 8-Ball Says: It is certain.</b>', '<b style="color:#7FEC11">The 8-Ball Says: It is decidedly so.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Without a doubt.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes definitely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: You may rely on it.</b>', '<b style="color:#7FEC11">The 8-Ball Says: As I see it, yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Most likely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Outlook good.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Signs point to yes.</b>', '<b style="color:#E7890C">The 8-Ball Says: Reply hazy, try again.</b>', '<b style="color:#E7890C">The 8-Ball Says: Ask again later.</b>', '<b style="color:#E7890C">The 8-Ball Says: Better not tell you now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Cannot predict now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Concentrate and ask again.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Don\'t count on it.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My reply is no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My sources say no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Outlook not so good.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Very doubtful.</b>')

REDDIT_NOTIFS_SITE = set()
REDDIT_NOTIFS_USERS = {}

if len(SITE_NAME) > 5:
	REDDIT_NOTIFS_SITE.add(SITE_NAME.lower())

if not IS_LOCALHOST:
	REDDIT_NOTIFS_SITE.add(SITE)

if SITE == 'rdrama.net':
	REDDIT_NOTIFS_SITE.add('marsey')
	REDDIT_NOTIFS_SITE.add('"r/Drama"')
	REDDIT_NOTIFS_SITE.add('justice4darrell')
	REDDIT_NOTIFS_USERS = {
		'idio3': IDIO_ID,
		'aevann': AEVANN_ID,
		'carpflo': CARP_ID,
		'carpathianflorist': CARP_ID,
		'carpathian florist': CARP_ID,
		'the_homocracy': HOMO_ID,
		'justcool393': JUSTCOOL_ID
	}
elif SITE_NAME == 'WPD':
	REDDIT_NOTIFS_SITE.update({'watchpeopledie', 'makemycoffin'})

discounts = {
	# Big Spender badges, 2pp additive discount each
	69: 0.02,
	70: 0.02,
	71: 0.02,
	72: 0.02,
	73: 0.02,
	# Lootbox badges, 1pp additive discount each
	76: 0.01,
	77: 0.01,
	78: 0.01,
}

CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

WORDLE_LIST = ('aaron','about','above','abuse','acids','acres','actor','acute','adams','added','admin','admit','adopt','adult','after','again','agent','aging','agree','ahead','aimed','alarm','album','alert','alias','alice','alien','align','alike','alive','allah','allan','allen','allow','alloy','alone','along','alpha','alter','amber','amend','amino','among','angel','anger','angle','angry','anime','annex','annie','apart','apple','apply','april','areas','arena','argue','arise','armed','armor','array','arrow','aruba','ascii','asian','aside','asked','asset','atlas','audio','audit','autos','avoid','award','aware','awful','babes','bacon','badge','badly','baker','balls','bands','banks','barry','based','bases','basic','basin','basis','batch','baths','beach','beads','beans','bears','beast','beats','began','begin','begun','being','belle','belly','below','belts','bench','berry','betty','bible','bikes','bills','billy','bingo','birds','birth','bitch','black','blade','blair','blake','blame','blank','blast','blend','bless','blind','blink','block','blogs','blond','blood','bloom','blues','board','boats','bobby','bonds','bones','bonus','boobs','books','boost','booth','boots','booty','bored','bound','boxed','boxes','brain','brake','brand','brass','brave','bread','break','breed','brian','brick','bride','brief','bring','broad','broke','brook','brown','bruce','brush','bryan','bucks','buddy','build','built','bunch','bunny','burke','burns','burst','buses','busty','butts','buyer','bytes','cabin','cable','cache','cakes','calif','calls','camel','camps','canal','candy','canon','cards','carey','cargo','carlo','carol','carry','cases','casey','casio','catch','cause','cedar','cells','cents','chain','chair','chaos','charm','chart','chase','cheap','cheat','check','chess','chest','chevy','chick','chief','child','chile','china','chips','choir','chose','chris','chuck','cindy','cisco','cited','civic','civil','claim','clara','clark','class','clean','clear','clerk','click','cliff','climb','clips','clock','clone','close','cloth','cloud','clubs','coach','coast','cocks','codes','cohen','coins','colin','colon','color','combo','comes','comic','condo','congo','const','coral','corps','costa','costs','could','count','court','cover','crack','craft','craig','craps','crash','crazy','cream','creek','crest','crime','crops','cross','crowd','crown','crude','cubic','curve','cyber','cycle','czech','daddy','daily','dairy','daisy','dance','danny','dated','dates','david','davis','deals','dealt','death','debug','debut','decor','delay','delhi','delta','dense','depot','depth','derby','derek','devel','devil','devon','diana','diane','diary','dicke','dicks','diego','diffs','digit','dildo','dirty','disco','discs','disks','dodge','doing','dolls','donna','donor','doors','doubt','dover','dozen','draft','drain','rDrama','drawn','draws','dream','dress','dried','drill','drink','drive','drops','drove','drugs','drums','drunk','dryer','dubai','dutch','dying','dylan','eagle','early','earth','ebony','ebook','eddie','edgar','edges','egypt','eight','elder','elect','elite','ellen','ellis','elvis','emacs','email','emily','empty','ended','endif','enemy','enjoy','enter','entry','epson','equal','error','essay','essex','euros','evans','event','every','exact','exams','excel','exist','extra','faced','faces','facts','fails','fairy','faith','falls','false','fancy','fares','farms','fatal','fatty','fault','favor','fears','feeds','feels','fence','ferry','fever','fewer','fiber','fibre','field','fifth','fifty','fight','filed','files','filme','films','final','finds','fired','fires','firms','first','fixed','fixes','flags','flame','flash','fleet','flesh','float','flood','floor','flour','flows','floyd','fluid','flush','flyer','focal','focus','folks','fonts','foods','force','forge','forms','forth','forty','forum','found','frame','frank','fraud','fresh','front','frost','fruit','fully','funds','funky','funny','fuzzy','gains','games','gamma','gates','gauge','genes','genre','ghana','ghost','giant','gifts','girls','given','gives','glass','glenn','globe','glory','gnome','goals','going','gonna','goods','gotta','grace','grade','grain','grams','grand','grant','graph','grass','grave','great','greek','green','grill','gross','group','grove','grown','grows','guard','guess','guest','guide','guild','hairy','haiti','hands','handy','happy','harry','haven','hayes','heads','heard','heart','heath','heavy','helen','hello','helps','hence','henry','herbs','highs','hills','hindu','hints','hired','hobby','holds','holes','holly','homes','honda','honey','honor','hoped','hopes','horny','horse','hosts','hotel','hours','house','human','humor','icons','idaho','ideal','ideas','image','inbox','index','india','indie','inner','input','intel','inter','intro','iraqi','irish','isaac','islam','issue','italy','items','ivory','jacob','james','jamie','janet','japan','jason','jeans','jenny','jerry','jesse','jesus','jewel','jimmy','johns','joins','joint','jokes','jones','joyce','judge','juice','julia','julie','karen','karma','kathy','katie','keeps','keith','kelly','kenny','kenya','kerry','kevin','kills','kinda','kinds','kings','kitty','klein','knife','knock','known','knows','kodak','korea','label','labor','laden','lakes','lamps','lance','lands','lanes','lanka','large','larry','laser','later','latex','latin','laugh','laura','layer','leads','learn','lease','least','leave','leeds','legal','lemon','leone','level','lewis','lexus','light','liked','likes','limit','linda','lined','lines','links','linux','lions','lists','lived','liver','lives','lloyd','loads','loans','lobby','local','locks','lodge','logan','logic','login','logos','looks','loops','loose','lopez','lotus','louis','loved','lover','loves','lower','lucas','lucia','lucky','lunch','lycos','lying','lyric','macro','magic','mails','maine','major','maker','makes','males','malta','mambo','manga','manor','maple','march','marco','mardi','maria','marie','mario','marks','mason','match','maybe','mayor','mazda','meals','means','meant','medal','media','meets','menus','mercy','merge','merit','merry','metal','meter','metro','meyer','miami','micro','might','milan','miles','milfs','mills','minds','mines','minor','minus','mixed','mixer','model','modem','modes','money','monte','month','moore','moral','moses','motel','motor','mount','mouse','mouth','moved','moves','movie','mpegs','msgid','multi','music','myers','nails','naked','named','names','nancy','nasty','naval','needs','nepal','nerve','never','newer','newly','niger','night','nikon','noble','nodes','noise','nokia','north','noted','notes','notre','novel','nurse','nylon','oasis','occur','ocean','offer','often','older','olive','omaha','omega','onion','opens','opera','orbit','order','organ','oscar','other','ought','outer','owned','owner','oxide','ozone','packs','pages','paint','pairs','panel','panic','pants','paper','papua','paris','parks','parts','party','pasta','paste','patch','paths','patio','paxil','peace','pearl','peers','penis','penny','perry','perth','peter','phase','phone','photo','phpbb','piano','picks','piece','pills','pilot','pipes','pitch','pixel','pizza','place','plain','plane','plans','plant','plate','plays','plaza','plots','poems','point','poker','polar','polls','pools','porno','ports','posts','pound','power','press','price','pride','prime','print','prior','prize','probe','promo','proof','proud','prove','proxy','pulse','pumps','punch','puppy','purse','pussy','qatar','queen','query','quest','queue','quick','quiet','quilt','quite','quote','races','racks','radar','radio','raise','rally','ralph','ranch','randy','range','ranks','rapid','rated','rates','ratio','reach','reads','ready','realm','rebel','refer','rehab','relax','relay','remix','renew','reply','reset','retro','rhode','rider','rides','ridge','right','rings','risks','river','roads','robin','robot','rocks','rocky','roger','roles','rolls','roman','rooms','roots','roses','rouge','rough','round','route','rover','royal','rugby','ruled','rules','rural','safer','sagem','saint','salad','salem','sales','sally','salon','samba','samoa','sandy','santa','sanyo','sarah','satin','sauce','saudi','saved','saver','saves','sbjct','scale','scary','scene','scoop','scope','score','scott','scout','screw','scuba','seats','seeds','seeks','seems','sells','sends','sense','serum','serve','setup','seven','shade','shaft','shake','shall','shame','shape','share','shark','sharp','sheep','sheer','sheet','shelf','shell','shift','shine','ships','shirt','shock','shoes','shoot','shops','shore','short','shots','shown','shows','sides','sight','sigma','signs','silly','simon','since','singh','sites','sixth','sized','sizes','skill','skins','skirt','skype','slave','sleep','slide','slope','slots','sluts','small','smart','smell','smile','smith','smoke','snake','socks','solar','solid','solve','songs','sonic','sorry','sorts','souls','sound','south','space','spain','spank','sparc','spare','speak','specs','speed','spell','spend','spent','sperm','spice','spies','spine','split','spoke','sport','spots','spray','squad','stack','staff','stage','stamp','stand','stars','start','state','stats','stays','steal','steam','steel','steps','steve','stick','still','stock','stone','stood','stops','store','storm','story','strap','strip','stuck','study','stuff','style','sucks','sudan','sugar','suite','suits','sunny','super','surge','susan','sweet','swift','swing','swiss','sword','syria','table','tahoe','taken','takes','tales','talks','tamil','tampa','tanks','tapes','tasks','taste','taxes','teach','teams','tears','teddy','teens','teeth','tells','terms','terry','tests','texas','texts','thank','thats','theft','their','theme','there','these','thick','thing','think','third','thong','those','three','throw','thumb','tiger','tight','tiles','timer','times','tions','tired','tires','title','today','token','tokyo','tommy','toner','tones','tools','tooth','topic','total','touch','tough','tours','tower','towns','toxic','trace','track','tract','tracy','trade','trail','train','trans','trash','treat','trees','trend','trial','tribe','trick','tried','tries','trips','trout','truck','truly','trunk','trust','truth','tubes','tulsa','tumor','tuner','tunes','turbo','turns','tvcom','twice','twiki','twins','twist','tyler','types','ultra','uncle','under','union','units','unity','until','upper','upset','urban','usage','users','using','usual','utils','valid','value','valve','vault','vegas','venue','verde','verse','video','views','villa','vinyl','viral','virus','visit','vista','vital','vocal','voice','volvo','voted','votes','vsnet','wages','wagon','wales','walks','walls','wanna','wants','waste','watch','water','watts','waves','wayne','weeks','weird','wells','welsh','wendy','whale','whats','wheat','wheel','where','which','while','white','whole','whore','whose','wider','width','wiley','winds','wines','wings','wired','wires','witch','wives','woman','women','woods','words','works','world','worry','worse','worst','worth','would','wound','wrist','write','wrong','wrote','xanax','xerox','xhtml','yacht','yahoo','yards','years','yeast','yemen','yield','young','yours','youth','yukon','zones','gypsy','etika','funko','abort','gabby','soros','twink','biden','janny','chapo','4chan','tariq','tweet','trump','bussy','sneed','chink','nigga','wigga','caulk','putin','negus','gussy','soren')

christian_emojis = [':#marseyjesus:',':#marseyimmaculate:',':#marseymothermary:',
	':#marseyfatherjoseph:',':#gigachadorthodox:',':#marseyorthodox:',':#marseyorthodoxpat:',
	':#marseycrucified:',':#chadjesus:',':#marseyandjesus:',':#marseyjesus2:',
	':#marseyorthodoxsmug:',':#marseypastor:',':#marseypope:',]

ADMIGGER_THREADS = {SIDEBAR_THREAD, BANNER_THREAD, BADGE_THREAD, SNAPPY_THREAD}

proxies = {"http":PROXY_URL,"https":PROXY_URL}

approved_embed_hosts = {
	SITE,
	'rdrama.net',
	BAN_EVASION_DOMAIN,
	'pcmemes.net',
	'watchpeopledie.tv',
	'imgur.com',
	'lain.la',
	'pngfind.com',
	'kym-cdn.com',
	'redd.it',
	'substack.com',
	'blogspot.com',
	'catbox.moe',
	'pinimg.com',
	'kindpng.com',
	'shopify.com',
	'twimg.com',
	'wikimedia.org',
	'wp.com',
	'wordpress.com',
	'seekpng.com',
	'dailymail.co.uk',
	'cdc.gov',
	'media-amazon.com',
	'ssl-images-amazon.com',
	'washingtonpost.com',
	'imgflip.com',
	'flickr.com',
	'9cache.com',
	'ytimg.com',
	'foxnews.com',
	'duckduckgo.com',
	'forbes.com',
	'gr-assets.com',
	'tenor.com',
	'giphy.com',
	'makeagif.com',
	'gfycat.com',
	'tumblr.com',
	'yarn.co',
	'gifer.com',
	'staticflickr.com',
	'kiwifarms.net',
	'amazonaws.com',
	'githubusercontent.com',
	'unilad.co.uk',
	'grrrgraphics.com',
	'redditmedia.com',
	'deviantart.com',
	'deviantart.net',
	'googleapis.com',
	'bing.com',
	'typekit.net',
	'postimg.cc',
	'archive.org',
	'substackcdn.com',
	'9gag.com',
	'ifunny.co',
	'wixmp.com',
	'derpicdn.net',
	'twibooru.org',
	'ponybooru.org',
	'e621.net',
	'ponerpics.org',
	'furaffinity.net'
	}


def is_site_url(url):
	return url and '\\' not in url and ((url.startswith('/') and not url.startswith('//')) or url.startswith(f'{SITE_FULL}/'))

def is_safe_url(url):
	return is_site_url(url) or tldextract.extract(url).registered_domain in approved_embed_hosts


hosts = "|".join(approved_embed_hosts).replace('.','\.')

tiers={
	"(Paypig)": 1,
	"(Renthog)": 2,
	"(Landchad)": 3,
	"(Terminally online turboautist)": 4,
	"(Marsey's Sugar Daddy)": 5,
	"(JIDF Bankroller)": 6,
	"(Rich Bich)": 7,
	"(LlamaBean)": 1,
	"(Victim)": 1,
	"(Corpse)": 2,
	"(Zombie)": 3,
	"(Ghost)": 4,
	"(Survivor)": 5,
	"(Jigsaw)": 6,
	}

has_sidebar = path.exists(f'files/templates/sidebar_{SITE_NAME}.html')
has_logo = path.exists(f'files/assets/images/{SITE_NAME}/logo.webp')

ONLINE_STR = f'{SITE}_online'

forced_hats = {
	"rehab": ("Roulette", "I'm a recovering ludomaniac!"),
	"progressivestack": ("Attention Whore", "I won the oppression olympics!"),
	"longpost": ("The Pizzashill", "We need to get rid of the character limit!"),
	"bird": ("Bluecheck", "Three sentences is too much for me..."),
	"marseyawarded": ("Three Lil Marseys", ":marseynotes: :marseynotes: :I prefer to speak in cats:"),
	"bite": ("Vampire Mask", "When other little girls wanted to be ballet dancers I kind of wanted to be a vampire."),
	"rainbow": ("Globohomo", "Homosexuality is no longer optional!"),
	"owoify": ("Cat Ears (wiggly)", "Nuzzles, pounces on you, UwU, you're so warm!.."),
	"earlylife": ("The Merchant", "SHUT IT DOWN, the goys know!"),
	"marsify": ("Marsified", "I can't pick my own Marseys, help!"),
	"is_suspended": ("Behind Bars", "This user is banned and needs to do better!"),
	"agendaposter": ("Egg_irl", "This user is getting in touch with xir identity!")
}

EMAIL_REGEX_PATTERN = '[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{2,63}\.[A-Za-z]{2,63}'

if SITE_NAME == 'rDrama':
	BOOSTED_SITES = {
		'rdrama.net',
		BAN_EVASION_DOMAIN,
		'pcmemes.net',
		'watchpeopledie.tv',
		'themotte.org',
		'quora.com',
		'cumtown.org',
		'notabug.io',
		'talk.lol',
		'discussions.app',
		'gab.com',
		'kiwifarms.net',
		'gettr.com',
		'scored.co',
		'parler.com',
		'bitchute.com',
		'4chan.org',
		'givesendgo.com',
		'thepinkpill.com',
		'ovarit.com',
		'rdrama.cc',
		'lolcow.farm',
		'truthsocial.com',
		'rumble.com',
		'saidit.net',
		'kiwifarms.cc',
		'8kun.top',
		'goyimtv.tv',
		'poal.co',
		'stormfront.org',
		'arete.network',
		'poa.st',
		'lbry.com',
		'crystal.cafe',
		'tribel.com',
		'mstdn.social',
		'mastodon.online',
		'steemit.com',
		'hexbear.net',
		'raddle.me',
		'lemmy.ml',
		'bluelight.org',
		'incels.is',
		'groups.google.com',
		't.me',
		'web.telegram.org',
		'news.ycombinator.com',
		'tigerdroppings.com',
		'instagram.com',
		'facebook.com',
		'twitch.tv',
		'tiktok.com',
		'vm.tiktok.com',
		'github.com',
		'boards.4channel.org',
		'boards.4chan.org',
		'archive.4plebs.org',
		'lipstickalley.com',
		'resetera.com',
		'steamcommunity.com',
		'nairaland.com',
		'marsey.club',
		'odysee.com',
		'trp.red',
		'forums.red',
		'shitposter.club',
		'sneed.social',
		'seal.cafe',
		'lobste.rs',
		'stacker.news',
		'breitbart.com',
		'tattle.life',
		'wolfballs.com',
		'backloggd.com',
		'tildes.net',
	}

	BOOSTED_HOLES = {
		'furry',
		'femboy',
		'anime',
		'gaybros',
		'againsthateholes',
		'masterbaiters',
		'changelog',
	}

	UNNERFED_HOLES = {
		'space',
		'istory',
		'dino',
		'slackernews',
		'schizocel',
	}

	BOOSTED_USERS = {
		IMPASSIONATA_ID,
		PIZZASHILL_ID,
		SNAKES_ID,
		JUSTCOOL_ID,
		2008, #TransGirlTradWife
	}

	BOOSTED_USERS_EXCLUDED = {8768, 5214, 12719, 3402}

IMAGE_FORMATS = ['png','gif','jpg','jpeg','webp']
VIDEO_FORMATS = ['mp4','webm','mov','avi','mkv','flv','m4v','3gp']
AUDIO_FORMATS = ['mp3','wav','ogg','aac','m4a','flac']
