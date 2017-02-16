#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/11/15 0015"
"""
from django.conf.urls import url

from wechat import views

urlpatterns = [
    # url(r"^message/$", views.TokenCheckView.as_view(), name='token_check'),
    url(r'^message/$', views.MessageView.as_view(),
        name='wechat_message'),
]