# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-08 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0022_auto_20161213_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatmenuconfig',
            name='level_2',
            field=models.ManyToManyField(blank=True, default=None, related_name='select_menus', to='wechat.WechatMenuSubConfig', verbose_name='耳机菜单'),
        ),
    ]
