#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/8/11"
"""
from utils.tools import close_db_connection
from wechat.models import RobotDetail

@close_db_connection
def wechat_reset_robot():
    RobotDetail.objects.filter(status=2).update(status=0)




