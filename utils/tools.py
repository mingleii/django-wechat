#!/usr/bin/env python
# coding=utf-8
import socket
import os
import pprint
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import functools
from collections import OrderedDict
from email.mime.text import MIMEText

import redis
import logging
from django.db import connection
from smallsite import settings


logger = logging.getLogger("default")

redis_ins = redis.Redis(
    host=settings.CACHES["default"]["LOCATION"][0].split(":")[0],
    port=settings.CACHES["default"]["LOCATION"][0].split(":")[1],
    db=settings.CACHES["default"]["OPTIONS"]["DB"],
    password=settings.REDIS_PASSWD,
    charset="utf-8", decode_responses=True)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_host_ip():
    # 获取服务器本地ip
    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip


def close_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            connection.close()
        except:
            import traceback
            errors = traceback.format_exc()
            logger.error("func_name:%s" % func.__name__,
                         extra={"error": errors})
    return wrapper

def custom_sql(sql, fetch_one=False, not_select=False, order_dict=False):
    """ sql直接查询
    :param sql: sql语句
    :param not_select: sql为非查询
    :param fetch_one:  默认 false 取全部, true 取1个
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        if not_select:
            return
        columns = [col[0] for col in cursor.description]
        if fetch_one:
            row = cursor.fetcone()
            res = dict(zip(columns, row))
        else:
            if not order_dict:
                res = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                    ]
            else:
                res = [
                    OrderedDict(zip(columns, row))
                    for row in cursor.fetchall()
                    ]
        return res

def try_except_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            import traceback
            errors = traceback.format_exc()
            logger.error("func_name:%s" % func.__name__,
                         extra={"error": errors})
    return wrapper

@try_except_log
def send_email(sub_enable, body, attach=None, images=None,
               title=settings.EMAIL_CONFIG["title"],
               sender=settings.EMAIL_CONFIG["sender"],
               receiver=settings.EMAIL_CONFIG["receiver"],
               server_ip=settings.EMAIL_CONFIG["server_ip"],
               server_port=settings.EMAIL_CONFIG["server_port"],
               username=settings.EMAIL_CONFIG["username"],
               passwd=settings.EMAIL_CONFIG["passwd"]):
    if (not settings.EMAIL_ENABLE) or (sub_enable not in settings.EMAIL_SUB_ENABLES):
        return False
    msg = MIMEMultipart()
    msg['Subject'] = Header(title, "utf-8")  # 设置邮件标题
    msg['From'] = sender  # 设置发件人
    if isinstance(receiver, str):
        msg['To'] = receiver  # 设置收件人
    else:
        msg['To'] = ";".join(receiver)  # 多个收件人

    # text_msg = MIMEText(content, _subtype="html", _charset="utf-8")
    #  设置正文为符合邮件格式的HTML内容
    text_msg = MIMEText(body)
    msg.attach(text_msg)

    if attach:
        for path, name in attach.items():
            if os.path.exists(path):
                att = MIMEText(open(path, 'rb').read(), 'base64', 'gb2312')   #构造附件
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment; filename="' + name + '"'
                msg.attach(att)

    if images:
        for path, name in images.items():
            if os.path.exists(path):
                image = MIMEImage(open(path,'rb').read())
                #image = MIMEImage(open(path,'rb').read(), _subtype="jpg")
                image.add_header("Content-Disposition", "attachment", filename=name)
                image.add_header('Content-ID', '<0>')
                image.add_header('X-Attachment-Id', '0')
                msg.attach(image)

    s = smtplib.SMTP(server_ip, server_port)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
    s.login(username, passwd)                      # 登陆邮箱
    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件
    logger.info("send_email_success",
                extra={"sender": sender, "receiver": receiver,
                       "sub_enable": sub_enable})
    return True


def to_human(dict_obj):
    pp = pprint.PrettyPrinter(indent=4)
    return pp.pformat(dict_obj)

def to_str(b_str):
    return str(b_str, encoding="utf-8")

