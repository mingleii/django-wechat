# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-29 18:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0015_auto_20161129_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wechatautoreply',
            name='code_key',
        ),
        migrations.AlterField(
            model_name='wechatautoreply',
            name='keyword',
            field=models.CharField(blank=True, default='', help_text='多个以【|】分割', max_length=255, verbose_name='关键字'),
        ),
    ]
