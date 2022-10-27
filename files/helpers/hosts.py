from .const import *

def current_host():
	# NB: apparently this is pretty broken in some cases so we're going
    # to just use SITE_FULL until it's figured out
	return SITE_FULL

	# if SITE == "localhost": prefix = "http://"
	# else: prefix = "https://"
	
	# if request.host not in SITE_HOSTS: return SITE_FULL
	# return prefix + request.host
