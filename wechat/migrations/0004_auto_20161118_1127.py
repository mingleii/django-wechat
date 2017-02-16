# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-18 11:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0003_auto_20161117_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatdetail',
            name='encrypt_mode',
            field=models.CharField(choices=[('normal', '明文模式'), ('compatible', '兼容模式'), ('safe', '安全模式（推荐）')], default='safe', help_text='<p>明文模式下，不使用消息体加解密功能，安全系数较低</p><p>兼容模式下，明文、密文将共存，方便开发者调试和维护</p><p>安全模式下，消息包为纯密文，需要开发者加密和解密，安全系数高</p>', max_length=36, verbose_name='消息加解密方式'),
        ),
    ]
