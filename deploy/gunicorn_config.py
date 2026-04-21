import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
proc_name = 'zjoj'
pidfile = '/var/run/zjoj/gunicorn.pid'
accesslog = '/var/log/zjoj/gunicorn_access.log'
errorlog = '/var/log/zjoj/gunicorn_error.log'
loglevel = 'info'
preload_app = True
max_requests = 1000
max_requests_jitter = 50
