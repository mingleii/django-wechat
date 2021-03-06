# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-25 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0008_auto_20161125_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='WechatUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscribe', models.BooleanField(default=True, verbose_name='是否订阅')),
                ('openid', models.CharField(max_length=36, unique=True, verbose_name='OpenID')),
                ('nickname', models.CharField(max_length=36, verbose_name='昵称')),
                ('sex', models.SmallIntegerField(choices=[(0, '未知'), (1, '男性'), (2, '女性')], verbose_name='性别')),
                ('city', models.CharField(max_length=36, verbose_name='城市')),
                ('country', models.CharField(max_length=36, verbose_name='国家')),
                ('province', models.CharField(max_length=36, verbose_name='省份')),
                ('language', models.CharField(max_length=36, verbose_name='语言')),
                ('headimgurl', models.CharField(max_length=255, verbose_name='用户头像')),
                ('subscribe_time', models.CharField(max_length=16, verbose_name='关注时间')),
                ('unionid', models.CharField(max_length=16, verbose_name='UnionID')),
                ('remark', models.CharField(max_length=16, verbose_name='备注名称')),
                ('group_id', models.IntegerField(verbose_name='GroupID')),
                ('ctime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('utime', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '微信用户',
                'db_table': 'wechat_user',
                'verbose_name_plural': '微信用户',
            },
        ),
        migrations.AlterField(
            model_name='wechatmenuconfig',
            name='is_online',
            field=models.BooleanField(choices=[(True, '上线'), (False, '下线')], default=True, verbose_name='是否上线'),
        ),
        migrations.AlterField(
            model_name='wechatmenusubconfig',
            name='is_display',
            field=models.BooleanField(choices=[(True, '显示'), (False, '消失')], default=True, verbose_name='是否可选'),
        ),
        migrations.AlterField(
            model_name='wechatmenusubconfig',
            name='wm_pos',
            field=models.SmallIntegerField(default=1, help_text='自定义菜单最多包括3个一级菜单，每个一级菜单最多包含5个二级菜单，数字：1-5', verbose_name='位置'),
        ),
        migrations.AlterField(
            model_name='wechatmenusubconfig',
            name='wm_type',
            field=models.CharField(blank=True, choices=[('', '（无内容）'), ('click', '点击推事件'), ('view', '跳转URL'), ('scancode_push', '扫码推事件'), ('scancode_waitmsg', '扫码推事件且弹出“消息接收中”提示框'), ('pic_sysphoto', '弹出系统拍照发图'), ('pic_photo_or_album', '弹出拍照或者相册发图'), ('pic_weixin', '弹出微信相册发图器'), ('location_select', '弹出地理位置选择器'), ('media_id', '下发消息（除文本消息）'), ('view_limited', '跳转图文消息URL')], default='', help_text='<a href="https://mp.weixin.qq.com/wiki" target="_blank">详细介绍</a>', max_length=36, verbose_name='菜单类型'),
        ),
    ]
