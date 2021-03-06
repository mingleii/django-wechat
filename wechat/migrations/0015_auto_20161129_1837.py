# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-29 18:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0014_auto_20161129_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatautoreply',
            name='is_online',
            field=models.BooleanField(choices=[(True, '上线'), (False, '下线')], default=False, verbose_name='是否上线'),
        ),
        migrations.AddField(
            model_name='wechatautoreply',
            name='is_valid',
            field=models.BooleanField(default=False, verbose_name='是否生效'),
        ),
        migrations.AlterField(
            model_name='wechatautoreply',
            name='reply_file',
            field=models.FileField(blank=True, default='', upload_to='private/wechat/msg_file/reply/', verbose_name='回复文件'),
        ),
        migrations.AlterField(
            model_name='wechatmessagelog',
            name='reply_file',
            field=models.FileField(blank=True, default='', upload_to='private/wechat/msg_file/reply/', verbose_name='回复文件'),
        ),
    ]
