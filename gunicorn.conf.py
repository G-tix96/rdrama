bind = '0.0.0.0:5000'

workers = 9
worker_class = 'gevent'

max_requests = 30000
max_requests_jitter = 30000

reload = True
reload_engine = 'poll'

def worker_abort(worker):
	worker.log.warning(f"Worker {worker.pid} received SIGABRT.")
	try:
		from flask import g, request
		if g and request:
			worker.log.warning(f"\n\nWhile serving {request.method} {request.url}")
			u = getattr(g, 'v', None)
			if u:
				worker.log.warning(f"User: {u.username!r} id:{u.id}\n\n")
			else:
				worker.log.warning(f"User: not logged in\n\n")
		else:
			worker.log.warning("No request info")
	except:
		worker.log.warning("Failed to get request info")

	import os
	os.abort()
