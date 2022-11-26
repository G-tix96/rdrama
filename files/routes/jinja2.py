import time

from os import environ, listdir, path

from jinja2 import pass_context

from files.classes.user import User
from files.helpers.assetcache import assetcache_path
from files.helpers.const import *
from files.helpers.settings import get_settings
from files.helpers.sorting_and_time import make_age_string
from files.routes.routehelpers import get_formkey
from files.routes.wrappers import calc_users
from files.__main__ import app, cache

@app.template_filter("formkey")
def formkey(u):
	return get_formkey(u)

@app.template_filter("post_embed")
def post_embed(id, v):
	from flask import render_template

	from files.helpers.get import get_post
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
	return make_age_string(timestamp)

@app.context_processor
def inject_constants():
	return {"environ":environ, "SITE":SITE, "SITE_NAME":SITE_NAME, "SITE_FULL":SITE_FULL,
			"AUTOJANNY_ID":AUTOJANNY_ID, "MODMAIL_ID":MODMAIL_ID, "PUSHER_ID":PUSHER_ID, 
			"CC":CC, "CC_TITLE":CC_TITLE, "listdir":listdir, "os_path":path, "AEVANN_ID":AEVANN_ID,
			"PIZZASHILL_ID":PIZZASHILL_ID, "DEFAULT_COLOR":DEFAULT_COLOR, 
			"COLORS":COLORS, "time":time, "PERMS":PERMS, "FEATURES":FEATURES,
			"HOLE_NAME":HOLE_NAME, "HOLE_STYLE_FLAIR":HOLE_STYLE_FLAIR, "HOLE_REQUIRED":HOLE_REQUIRED,
			"GUMROAD_LINK":GUMROAD_LINK, "DEFAULT_THEME":DEFAULT_THEME, "DESCRIPTION":DESCRIPTION,
			"has_sidebar":has_sidebar, "has_logo":has_logo,
			"FP":FP, "cache":cache, "ONLINE_STR":ONLINE_STR, "patron":patron, "DUES":DUES,
			"SIDEBAR_THREAD":SIDEBAR_THREAD, "BANNER_THREAD":BANNER_THREAD,
			"BADGE_THREAD":BADGE_THREAD, "SNAPPY_THREAD":SNAPPY_THREAD,
			"KOFI_TOKEN":KOFI_TOKEN, "KOFI_LINK":KOFI_LINK,
			"approved_embed_hosts":approved_embed_hosts,
			"site_settings":get_settings(), "EMAIL":EMAIL, "calc_users":calc_users, 
			"max": max, "min": min, "user_can_see":User.can_see,
			"TELEGRAM_LINK":TELEGRAM_LINK, "EMAIL_REGEX_PATTERN":EMAIL_REGEX_PATTERN,
			"CONTENT_SECURITY_POLICY_DEFAULT":CONTENT_SECURITY_POLICY_DEFAULT,
			"CONTENT_SECURITY_POLICY_HOME":CONTENT_SECURITY_POLICY_HOME,
			"TRUESCORE_DONATE_MINIMUM":TRUESCORE_DONATE_MINIMUM,
			"DONATE_LINK":DONATE_LINK, "DONATE_SERVICE":DONATE_SERVICE, "BAN_EVASION_DOMAIN":BAN_EVASION_DOMAIN, 
			"HOUSE_JOIN_COST":HOUSE_JOIN_COST, "HOUSE_SWITCH_COST":HOUSE_SWITCH_COST, "IMAGE_FORMATS":IMAGE_FORMATS,
			"PAGE_SIZES":PAGE_SIZES, "THEMES":THEMES, "COMMENT_SORTS":COMMENT_SORTS, "SORTS":SORTS, 
			"TIME_FILTERS":TIME_FILTERS, "HOUSES":HOUSES, "TIERS_ID_TO_NAME":TIERS_ID_TO_NAME, 
			"DEFAULT_CONFIG_VALUE":DEFAULT_CONFIG_VALUE, "IS_LOCALHOST":IS_LOCALHOST,
			}
