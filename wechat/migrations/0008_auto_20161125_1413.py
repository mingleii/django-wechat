# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-25 14:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0007_auto_20161125_1413'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wechatmenuconfig',
            options={'verbose_name': '菜单配置', 'verbose_name_plural': '菜单配置'},
        ),
        migrations.AlterModelTable(
            name='wechatmenuconfig',
            table='wechat_menu',
        ),
    ]
