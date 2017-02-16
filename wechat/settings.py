#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/11/18 0018"
"""
from smallsite import settings

WECHAT_CONFIG_KEYS = "wechat_congfig_info"

WECHAT_AUTO_REPLY_KEY = "auto_reply_"

WECHAT_ENCRYPT_MODE_CHOICE = (
    ("normal", "明文模式"),
    ("compatible", "兼容模式"),
    ("safe", "安全模式（推荐）")
)

SERVER_STATUS = (
    (-1, "废弃"),
    (0, "备用"),
    (1, "启用"),
    (2, "暂停"),
)

WECHAT_MENU_TYPE_CHOICE = (
    ("", "（无内容）"),
    ("click", "点击推事件"),
    ("view", "跳转URL"),
    ("scancode_push", "扫码推事件"),
    ("scancode_waitmsg", "扫码推事件且弹出“消息接收中”提示框"),
    ("pic_sysphoto", "弹出系统拍照发图"),
    ("pic_photo_or_album", "弹出拍照或者相册发图"),
    ("pic_weixin", "弹出微信相册发图器"),
    ("location_select", "弹出地理位置选择器"),
    ("media_id", "下发消息（除文本消息）"),
    ("view_limited", "跳转图文消息URL"),
)

WECHAT_MENU_TYPE_RELATED = {
    "": "",
    "click": "key",
    "view": "url",
    "scancode_push": "key",
    "scancode_waitmsg": "key",
    "pic_sysphoto": "key",
    "pic_photo_or_album": "key",
    "pic_weixin": "key",
    "location_select": "key",
    "media_id": "media_id",
    "view_limited": "media_id",
}

IS_ONLINE_CHOICE = (
    (True, "上线"),
    (False, "下线")
)

IS_DISPLAY_CHOICE = (
    (True, "显示"),
    (False, "消失")
)

WECHAT_MESSAGE_TYPE = (
    ("text", "文本消息"),
    ("voice", "语音消息"),
    ("image", "图片消息"),
    ("video", "视频消息"),
    ("shortvideo", "小视频消息"),
    ("link", "链接消息"),
    ("location", "发送位置消息"),
)

WECHAT_EVENT_TYPE = (
    ("click", "点击事件"),
    ("subscribe#new", "首次关注事件"),
    ("subscribe#old", "再次关注事件"),
    ("unsubscribe", "取消关注事件"),
    ("scan", "已关注扫描事件"),
    ("location", "地理位置事件"),
    ("view", "跳转链接事件"),
    ("templatesendjobfinish", "模板消息事件"),
)
WECHAT_EVENT_TYPE_RELATED = {
    "click": [],
    "subscribe#new": [],
    "subscribe#old": [],
    "unsubscribe": [],
    "scan": [],
    "location": [],
    "view": [],
    "templatesendjobfinish": [],
}

WECHAT_ALL_MSG_TYPE = WECHAT_MESSAGE_TYPE + (
    (-999, "--以下为事件消息--"),) + WECHAT_EVENT_TYPE


WECHAT_MESSAGE_TYPE_RELATED = {
    "text": ("content", ),
    "image": ("media_id", "picurl"),
    "voice": ("media_id", "format", "recognition"),
    "video": ("media_id", "thumb_media_id"),
    "shortvideo": ("media_id", "thumb_media_id"),
    "link": ("title", "description", "url"),
    "location": ("location", "scale", "label")
}

WECHAT_SEND_MESSAGE_TYPE = (
    ("text", "文本消息"),
    ("voice", "语音消息"),
    ("image", "图片消息"),
    ("video", "视频消息"),
    ("music", "音乐消息"),
    ("news", "图文消息"),
)

WECHAT_MEDIA_TYPE = {
    "image": [".jpg", ".gif", ".png "],  # 1M，支持JPG格式
    "voice": [".amr", ".mp3"],  # 2M，播放长度不超过60s，支持AMR\MP3格式
    "video": [".mp4"],  # 10MB，支持MP4格式
    "thumb": [".jpg"],  # 64KB，支持JPG格式
}

PRIORITY_CHOICE = (
    (0, "最低"),
    (1, "低"),
    (2, "较低"),
    (3, "中"),
    (4, "较高"),
    (5, "高"),
    (6, "最高")
)

ROBOT_PROVIDER_CHOICE = (
    ("tuling", "图灵机器人"),
)

ROBOT_PROVIDER_RELATED = {
    "tuling": "http://www.tuling123.com/openapi/api"
}