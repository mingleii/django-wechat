# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-30 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0017_auto_20161130_1224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wechatautoreply',
            name='weight',
        ),
        migrations.AddField(
            model_name='wechatautoreply',
            name='priority',
            field=models.SmallIntegerField(choices=[(0, '最低'), (1, '低'), (2, '较低'), (3, '中'), (4, '较高'), (5, '高'), (6, '最高')], default=0, help_text='数值越大规则越优先，范围：【0-99】', verbose_name='优先级'),
        ),
    ]
