from files.__main__ import app, cache
from jinja2 import pass_context
from .get import *
from os import listdir, environ
from .const import * 
import time
from files.helpers.assetcache import assetcache_path

@app.template_filter("post_embed")
def post_embed(id, v):
	p = get_post(id, v, graceful=True)
	
	if p: return render_template("submission_listing.html", listing=[p], v=v)
	return ''


@app.template_filter("asset")
@pass_context
def template_asset(ctx, asset_path):
	return assetcache_path(asset_path)


@app.template_filter("asset_siteimg")
def template_asset_siteimg(asset_path):
	# TODO: Add hashing for these using files.helpers.assetcache
	return f'/i/{SITE_NAME}/{asset_path}?v=3010'


@app.template_filter("timestamp")
def timestamp(timestamp):

	age = int(time.time()) - timestamp

	if age < 60:
		return "just now"
	elif age < 3600:
		minutes = int(age / 60)
		return f"{minutes}m ago"
	elif age < 86400:
		hours = int(age / 3600)
		return f"{hours}hr ago"
	elif age < 2678400:
		days = int(age / 86400)
		return f"{days}d ago"

	now = time.gmtime()
	ctd = time.gmtime(timestamp)

	months = now.tm_mon - ctd.tm_mon + 12 * (now.tm_year - ctd.tm_year)
	if now.tm_mday < ctd.tm_mday:
		months -= 1

	if months < 12:
		return f"{months}mo ago"
	else:
		years = int(months / 12)
		return f"{years}yr ago"


@app.context_processor
def inject_constants():
	return {"environ":environ, "SITE":SITE, "SITE_NAME":SITE_NAME, "SITE_FULL":SITE_FULL,
			"AUTOJANNY_ID":AUTOJANNY_ID, "PUSHER_ID":PUSHER_ID, 
			"CC":CC, "CC_TITLE":CC_TITLE, "listdir":listdir, "AEVANN_ID":AEVANN_ID, 
			"PIZZASHILL_ID":PIZZASHILL_ID, "DEFAULT_COLOR":DEFAULT_COLOR, 
			"COLORS":COLORS, "time":time, "PERMS":PERMS, "FEATURES":FEATURES,
			"HOLE_NAME":HOLE_NAME, "HOLE_STYLE_FLAIR":HOLE_STYLE_FLAIR, "HOLE_REQUIRED":HOLE_REQUIRED,
			"CASINO_ENABLED":CASINO_ENABLED, "GUMROAD_LINK":GUMROAD_LINK,
			"DEFAULT_THEME":DEFAULT_THEME, "DESCRIPTION":DESCRIPTION,
			"has_sidebar":has_sidebar, "has_logo":has_logo, "has_app":has_app,
			"FP":FP, "NOTIF_MODACTION_JL_MIN":NOTIF_MODACTION_JL_MIN, "cache":cache,
			"ONLINE_STR":ONLINE_STR, "patron":patron, "dues":dues,
			"SIDEBAR_THREAD":SIDEBAR_THREAD, "BANNER_THREAD":BANNER_THREAD,
			"BADGE_THREAD":BADGE_THREAD, "SNAPPY_THREAD":SNAPPY_THREAD,
			"KOFI_TOKEN":KOFI_TOKEN, "KOFI_LINK":KOFI_LINK,
			"approved_embed_hosts":approved_embed_hosts,
			"site_settings":app.config['SETTINGS'],
			"MAIL_USERNAME":app.config['MAIL_USERNAME'],
			}
