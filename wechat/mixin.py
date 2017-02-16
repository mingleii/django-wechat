#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/11/17 0017"
"""
import time
import datetime
import json
import logging
from collections import OrderedDict

from utils.tools import redis_ins, send_email, to_human
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.messages import TextMessage, VoiceMessage, ImageMessage, \
    VideoMessage, LinkMessage, LocationMessage, EventMessage, ShortVideoMessage

from wechat.models import WechatDetail, WechatUser, WechatMessageLog, \
    RobotDetail
from wechat.tools import GetWechat, MsgRobot
from wechat.settings import WECHAT_CONFIG_KEYS, WECHAT_MESSAGE_TYPE, \
    WECHAT_MESSAGE_TYPE_RELATED, WECHAT_AUTO_REPLY_KEY

logger = logging.getLogger("default")


class AutoReplyMsg(object):

    def record_msg(self, message):
        if message.type not in WECHAT_MESSAGE_TYPE_RELATED:
            # msg_type = "other"
            logger.info("wechat_record_message_other_type",
                        extra={"msg_type": message.type})
            return None, None
        msg_type = message.type
        content = {}
        for each in WECHAT_MESSAGE_TYPE_RELATED[msg_type]:
            content[each] = getattr(message, each)
        msg_data = to_human(content)
        try:
            wx_user = WechatUser.objects.get(openid=message.source)
        except WechatUser.DoesNotExist:
            logger.error("wechat_record_message_get_user_error",
                         extra={"msg_type": message.type,
                                "openid": message.source,
                                "content": content})
            return None, None
        wx_msg_log_obj = WechatMessageLog.objects.create(
            wx_user=wx_user, msg_type=msg_type, msg=msg_data)
        return wx_user.id, wx_msg_log_obj.id

    def __save_reply_msg(self, msg_log_id, reply_msg):
        try:
            msg_log_obj = WechatMessageLog.objects.get(id=msg_log_id)
        except WechatMessageLog.DoesNotExist:
            pass
        else:
            msg_log_obj.reply_msg = reply_msg
            msg_log_obj.is_replied = True
            msg_log_obj.save()

    def __get_robot(self, dis_robot_id=None):
        """dis_robot_id：已不可用的 robot_id"""
        if dis_robot_id:
            try:
                dis_robot_obj = RobotDetail.objects.get(id=dis_robot_id)
            except RobotDetail.DoesNotExist:
                logger.error("wechat_change_robot_obj_no_find",
                             extra={"robot_id": dis_robot_id})
            except RobotDetail.MultipleObjectsReturned:
                logger.error("wechat_change_robot_obj_find_many",
                             extra={"robot_id": dis_robot_id})
            else:
                dis_robot_obj.status = 2
                dis_robot_obj.save()
        bot_query = RobotDetail.objects.filter(status=1).order_by(
            "-priority")
        if bot_query.exists():
            return bot_query.first()
        ready_bot_query = RobotDetail.objects.filter(status=0).order_by(
            "-priority")
        if ready_bot_query.exists():
            read_robot_obj = ready_bot_query.first()
            read_robot_obj.status = 1
            read_robot_obj.save()
            return read_robot_obj
        return None

    def robot_reply_msg(self, message, **kwargs):
        if message.type == "text":
            bot_obj = self.__get_robot()
            if not bot_obj:
                return
            reply_msg = ""
            while True:
                msg_bot_obj = MsgRobot(bot_obj.provider, bot_obj.api_key)
                reply_msg = msg_bot_obj.get_answer(message.content,
                                                   kwargs.get("user_id"))
                if msg_bot_obj.msg_result[0] != -2:
                    break
                bot_obj = self.__get_robot(bot_obj.id)
                if not bot_obj:
                    return
            if kwargs.get("msg_log_id"):
                self.__save_reply_msg(kwargs["msg_log_id"], reply_msg)
            return reply_msg

    def event_reply_msg(self, message, **kwargs):
        if message.type not in WECHAT_MESSAGE_TYPE_RELATED:
            redis_key = WECHAT_AUTO_REPLY_KEY + "event"
            logger.info("wechat_record_message_other_type",
                        extra={"msg_type": message.type})
            redis_data = redis_ins.hget(redis_key, message.type)
            if redis_data:
                redis_json = json.loads(redis_data)
                reply_msg = redis_json.get(kwargs.get("event_key", ""))
                if reply_msg:
                    return reply_msg
            return "未匹配的事件消息，请联系管理员添加规则！"

    def default_reply_msg(self, message, **kwargs):
        if message.type in WECHAT_MESSAGE_TYPE_RELATED:
            redis_key = WECHAT_AUTO_REPLY_KEY + message.type
            reply_list = redis_ins.zrange(redis_key, 0, -1, desc=True)
            reply_msg = None
            for each_reply_json in reply_list:
                each_reply_dict = json.loads(each_reply_json)
                for keyword, msg in each_reply_dict.items():
                    if message.type == "text":
                        if keyword in message.content.lower():
                            reply_msg = msg
                            break
                    else:
                        reply_msg = msg
                        break
                if reply_msg:
                    if kwargs.get("msg_log_id"):
                        self.__save_reply_msg(kwargs["msg_log_id"], reply_msg)
                    return reply_msg


class MessageHandleMixin(AutoReplyMsg):
    
    def __init__(self, *args, **kwargs):
        self.__token = None
        self.__app_id = None
        self.__app_secret = None
        self.__encrypt_mode = None
        self.__encoding_aes_key = None
        self.__access_token = None
        self.__access_token_expires_at = None
        self.get_wechat = GetWechat()
        self.wechat = self.get_wechat.wechat_obj
        super(MessageHandleMixin, self).__init__()

    def general_reply_msg(self, message, user_id, msg_log_id):
        if message.type not in WECHAT_MESSAGE_TYPE_RELATED:
            return
        auto_reply_list = [self.default_reply_msg,
                           self.robot_reply_msg]
        for func in auto_reply_list:
            result = func(message, user_id=user_id, msg_log_id=msg_log_id)
            if result:
                return result
        return "未匹配到任何规则，管理员将会在后台查看并回复！"

    def msg_handle(self, message):
        response = None
        wx_user_id, wx_msg_log_id = self.record_msg(message)
        content = self.general_reply_msg(message, wx_user_id, wx_msg_log_id)
        if isinstance(message, TextMessage):
            # 文本消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, VoiceMessage):
            # 语音消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, ImageMessage):
            # 图片消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, VideoMessage):
            # 视频消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, ShortVideoMessage):
            # 小视频消息类
            response = self.wechat.response_text(content=content)
        elif isinstance(message, LinkMessage):
            # 链接消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, LocationMessage):
            # 发送位置消息
            response = self.wechat.response_text(content=content)
        elif isinstance(message, VoiceMessage):
            # 语音消息类
            response = self.wechat.response_text(content=content)
        elif isinstance(message, EventMessage):
            # 事件信息
            msg = self.__event_message(message)
            if not msg:
                msg = "谢谢您的回复~事件信息"
            response = self.wechat.response_text(content=msg)
        return response

    def save_user_info(self, openid):
        if self.get_wechat.conf["is_auth"]:
            user_info = self.wechat.get_user_info(openid)
        else:
            user_info = {"openid": openid}
        logger.info("wechat_save_user",
                    extra={"user_info": user_info})
        wx_user_data = {
            "nickname": user_info.get("nickname", ""),
            "sex": user_info.get("sex", 0),
            "city": user_info.get("city", ""),
            "country": user_info.get("country", ""),
            "province": user_info.get("province", ""),
            "language": user_info.get("language", ""),
            "headimgurl": user_info.get("headimgurl", ""),
            "subscribe_time": user_info.get("subscribe_time", ""),
            "unionid": user_info.get("unionid", ""),
            "remark": user_info.get("remark", ""),
            "group_id": user_info.get("group_id", 0)
        }
        wx_user, created = WechatUser.objects.get_or_create(
            openid=user_info["openid"], defaults=wx_user_data)
        return wx_user, created, user_info

    def __event_message(self, message):
        if message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
            key = message.key  # 对应于 XML 中的 EventKey (普通关注事件时此值为 None)
            ticket = message.ticket  # 对应于 XML 中的 Ticket (普通关注事件时此值为 None)
            wx_user, created, user_info = self.save_user_info(message.source)
            if not created:
                wx_user.subscribe = True
                wx_user.save()
                # return_msg = "亲爱的{nickname}，欢迎您再次关注~" \
                #              "".format(nickname=wx_user.nickname)
                message.type += "#old"
                reply_msg = self.event_reply_msg(message).format(
                    nickname=wx_user.nickname)
                send_email("wechat_old_user", to_human(user_info),
                           "公共号老用户再次关注消息")
            else:
                # reply_msg = "亲爱的{nickname}，感谢您首次关注~" \
                #              "".format(nickname=wx_user.nickname)
                message.type += "#new"
                reply_msg = self.event_reply_msg(message).format(
                    nickname=wx_user.nickname)
                send_email("wechat_new_user", to_human(user_info),
                           "公共号新用户关注消息")
            return reply_msg
        elif message.type == 'unsubscribe':  # 取消关注事件（无可用私有信息）
            logger.info("wechat_event_unsubscribe",
                        extra={"openid": message.source})
            wx_user = WechatUser.objects.get(openid=message.source)
            wx_user.is_subscribe=False
            wx_user.save()
            return
        elif message.type == 'scan':  # 用户已关注时的二维码扫描事件
            key = message.key  # 对应于 XML 中的 EventKey
            ticket = message.ticket  # 对应于 XML 中的 Ticket
        elif message.type == 'location':  # 上报地理位置事件
            latitude = message.latitude  # 对应于 XML 中的 Latitude
            longitude = message.longitude  # 对应于 XML 中的 Longitude
            precision = message.precision  # 对应于 XML 中的 Precision
        elif message.type == 'click':  # 自定义菜单点击事件
            key = message.key  # 对应于 XML 中的 EventKey
            reply_msg = self.event_reply_msg(message, event_key=key)
            return reply_msg
        elif message.type == 'view':  # 自定义菜单跳转链接事件
            key = message.key  # 对应于 XML 中的 EventKey
        elif message.type == 'templatesendjobfinish':  # 模板消息事件
            status = message.status  # 对应于 XML 中的 Status
        elif message.type in ['scancode_push', 'scancode_waitmsg',
                              'pic_sysphoto',
                              'pic_photo_or_album', 'pic_weixin',
                              'location_select']:  # 其他事件
            key = message.key  # 对应于 XML 中的 EventKey
