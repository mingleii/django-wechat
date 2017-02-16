#!/usr/bin/env python
# coding=utf-8

import multiprocessing
# import gevent.monkey

# gevent.monkey.patch_all()

debug = False
bind = '127.0.0.1:8808'
# bind = 'unix:/var/run/smallsite.sock'
max_requests = 1000
keepalive = 2

proc_name = 'smallsite'

workers = multiprocessing.cpu_count() + 1
# workers = 2
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

# worker_class = 'gaiohttp'

loglevel = 'info'
errorlog = '-'

x_forwarded_for_header = 'X-FORWARDED-FOR'
