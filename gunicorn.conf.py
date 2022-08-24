bind = '0.0.0.0:5000'

workers = 9
worker_class = 'gevent'

max_requests = 30000
max_requests_jitter = 30000

reload = True
#print_config = True

def worker_abort(worker):
	worker.log.warning(f"Worker {worker.pid} received SIGABRT.")

	try:
		import flask
		r = flask.request
		worker.log.warning(f"While serving {r.method} {r.url}")
		from files.helpers.wrappers import get_logged_in_user
		u = get_logged_in_user()
		if u:
			worker.log.warning(f"User: {u.username!r} id:{u.id}")
		else:
			worker.log.warning(f"User: not logged in")
	except:
		worker.log.warning("No request info")

	import os
	os.abort()

