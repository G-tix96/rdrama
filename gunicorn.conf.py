bind = '0.0.0.0:5000'

workers = 9
worker_class = 'gevent'

max_requests = 30000
max_requests_jitter = 30000

reload = True
#print_config = True

def worker_abort(worker):
	import os
	worker.log.info("Worker %s received SIGABRT." % worker.pid)
	os.abort()

