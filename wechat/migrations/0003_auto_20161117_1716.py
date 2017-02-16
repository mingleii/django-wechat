# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-17 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0002_auto_20161117_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatdetail',
            name='url',
            field=models.CharField(default='http://www.smallsite.cn/wechat/', max_length=255, verbose_name='服务器地址'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wechatdetail',
            name='status',
            field=models.SmallIntegerField(choices=[(-1, '废弃'), (0, '备用'), (1, '启用')], default=0, verbose_name='状态'),
        ),
    ]