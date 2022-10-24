from .const import *

def current_host():
	if SITE == "localhost": prefix = "http://"
	else: prefix = "https://"
	
	if request.host not in SITE_HOSTS: return SITE_FULL
	return prefix + request.host
