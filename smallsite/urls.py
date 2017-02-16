"""smallsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import logging

import time
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from django.contrib import admin
from django.conf.urls import url, include
from django.views.static import serve
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from smallsite import settings
from trial.processing import apscheduler_heart_beat
from utils.tools import send_email
from wechat.processing import wechat_reset_robot

logger = logging.getLogger("default")

urlpatterns = [
    url(r'^wechat/', include('wechat.urls', namespace='wechat',
                             app_name='wechat')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT},
        name="media"),
]


if settings.BACKEND_SERVER:
    urlpatterns += [
        url(r'^backend/', include(admin.site.urls)),
    ]

if settings.APSCHEDULER:
    logger.info("scheduler_started")

if settings.APSCHEDULER:
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = "".join([time.strftime("%y%m"), "9"])
        sock.bind(("127.0.0.1", int(port)))
    except socket.error:
        logger.info("scheduler_already_started, DO NOTHING")
    else:
        def job_listener(event):
            if event.exception:
                logger.info('apscheduler_job_crashed',
                            extra={"event": str(event.job_id),
                                   "exception": str(event.exception),
                                   "traceback": str(event.traceback)})

        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60
        }
        job_store = RedisJobStore(
            host=settings.CACHES["default"]["LOCATION"][0].split(":")[0],
            port=settings.CACHES["default"]["LOCATION"][0].split(":")[1],
            db=settings.CACHES["default"]["OPTIONS"]["DB"])
        jobstores = {
            'default': job_store,
        }

        # pro_scheduler = GeventScheduler()
        # pro_scheduler.add_listener(job_listener,
        #                            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        # pro_scheduler.add_job(apscheduler_heart_beat, 'interval', seconds=10,
        #                       kwargs={"obj": "pro_scheduler"},
        #                       id="pro_scheduler_heart_beat", replace_existing=True)
        # pro_scheduler.start()

        scheduler = BackgroundScheduler(jobstores=jobstores,
                                        executors=executors,
                                        job_defaults=job_defaults,
                                        timezone='Asia/Shanghai')
        scheduler.add_listener(job_listener,
                               EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.add_job(apscheduler_heart_beat, 'interval',
                          seconds=300,
                          kwargs={"obj": "scheduler"},
                          id="scheduler_heart_beat", replace_existing=True)
        scheduler.add_job(wechat_reset_robot, "cron",
                          hour=0, minute=1, second=1,
                          id="scheduler_heart_beat", replace_existing=True)
        scheduler.start()
        logger.info("apscheduler_add_job_over")
