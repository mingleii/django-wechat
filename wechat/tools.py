#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/11/25 0025"
"""
import logging
import os

import time

import requests
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.exceptions import OfficialAPIError

from utils.tools import redis_ins, to_str
from wechat.models import WechatDetail, WechatMenuConfig
from wechat.settings import WECHAT_CONFIG_KEYS, WECHAT_MENU_TYPE_RELATED, \
    WECHAT_MEDIA_TYPE, ROBOT_PROVIDER_RELATED

logger = logging.getLogger("default")


class GetWechat(object):

    def __init__(self):
        self.conf = {}
        self.__core_conf = {}
        self.__config_auto_refresh()
        self.__config_get_data()

    @property
    def config_obj(self):
        self.__config_auto_refresh()
        return WechatConf(**self.conf)

    @property
    def wechat_obj(self):
        return WechatBasic(conf=self.config_obj)

    def __config_auto_refresh(self, reduce_sec=600):
        if redis_ins.exists(WECHAT_CONFIG_KEYS):
            expires_at = int(redis_ins.hget(
                WECHAT_CONFIG_KEYS, "access_token_expires_at"))
            now_time = time.time()
            if expires_at <= now_time - reduce_sec:
                GetWechat.refresh_config_redis()
                self.__config_get_data()
        else:
            GetWechat.refresh_config_redis()
            self.__config_get_data()

    def __config_get_data(self):
        core_keys = ["token", "appid", "appsecret", "encrypt_mode",
                     "encoding_aes_key", "access_token", "access_token_expires_at"]
        self.conf = redis_ins.hgetall(WECHAT_CONFIG_KEYS)
        self.conf["access_token_expires_at"] = int(self.conf["access_token_expires_at"])
        self.conf["status"] = int(self.conf["status"])
        self.conf["is_auth"] = True if self.conf["is_auth"] == "True" else False
        for key, value in self.conf.items():
            if key in core_keys:
                self.__core_conf[key] = value

    @staticmethod
    def refresh_config_redis(original_id=None):
        if original_id:
            wechat_obj = WechatDetail.objects.get(original_id=original_id)
        else:
            wechat_obj = WechatDetail.objects.filter(status=1).first()
        core_data = wechat_obj.get_core()
        conf_obj = WechatConf(**core_data)
        expires_at = int(time.time()) + 60 * 60 * 2
        all_data = wechat_obj.get_all()
        all_data.update({"access_token": conf_obj.access_token,
                         "access_token_expires_at": expires_at})
        for key, value in all_data.items():
            redis_ins.hset(WECHAT_CONFIG_KEYS, key, value)
    logger.info("refresh_config_redis_success")

    @property
    def menu(self):
        try:
            menu_dict = self.wechat_obj.get_menu()
        except OfficialAPIError:
            return {"menu": "no exist hint"}
        return menu_dict


class SetWechat(GetWechat):

    def menu(self):
        menu_query = WechatMenuConfig.objects.filter(is_online=True
                                                     ).order_by("level_1__wm_pos")
        if menu_query:
            menu_dict = {}
            buttons = []
            for obj in menu_query:
                btn = {}
                btn["name"] = obj.level_1.wm_title
                btn["sub_button"] = []
                btn["type"] = obj.level_1.wm_type
                if btn["type"]:
                    btn[WECHAT_MENU_TYPE_RELATED[btn["type"]]] = obj.level_1.wm_key
                else:
                    del btn["type"]
                    l2_btn = {}
                    if obj.level_2.exists():
                        l2_query = obj.level_2.order_by("wm_pos")
                        for l2_obj in l2_query:
                            l2_btn["name"] = l2_obj.wm_title
                            l2_btn["type"] = l2_obj.wm_type
                            l2_btn[WECHAT_MENU_TYPE_RELATED[l2_btn["type"]]] = l2_obj.wm_key
                            l2_btn["sub_button"] = []
                            btn["sub_button"].append(l2_btn)
                buttons.append(btn)
            menu_dict["button"] = buttons
            logger.info("wechat_create_menu", extra=menu_dict)
            self.wechat_obj.create_menu(menu_dict)
            return menu_dict
        else:
            menu_dict = self.wechat_obj.get_menu()
            logger.info("wechat_delete_menu", extra=menu_dict)
            self.wechat_obj.delete_menu()
            return menu_dict

    def delete_menu(self):
        return self.wechat_obj.delete_menu()


def get_media_type(filename):
    ext_name = os.path.splitext(filename)[1]
    for type, file_exts in WECHAT_MEDIA_TYPE.items():
        if ext_name.lower() in file_exts:
            return type


class MsgRobot(object):
    # 错误类
    # -6: requests_error
    # -5: requests_not_200
    # -4: 40001 参数key错误
    # -3: 40002 请求内容info为空
    # -2: 40004 当天请求次数已使用完
    # -1: 40007 数据格式异常/请按规定的要求进行加密
    def __init__(self, provider, api_key, limit=10, is_secret=False, secret=None):
        self.__api_key = api_key
        self.__is_secret = is_secret
        self.secret = secret
        self.__provider = provider
        self.msg_result = (1, "get_msg_success")
        self.answer_dict = {}
        self.answer_msg = ""
        self.__limit = limit

    def __requests(self, question, user_id):
        req_data = {"key": self.__api_key,
                    "info": question}
        if user_id:
            req_data.update({"userid": str(user_id)})
        url = ROBOT_PROVIDER_RELATED[self.__provider]
        try:
            web_data = requests.post(url, json=req_data, timeout=5)
        except:
            result_msg = "robot_requests_error:%s_%s" % (self.__provider, self.__api_key)
            self.msg_result = (-6, result_msg)
        else:
            if web_data.status_code != 200:
                result_msg = "robot_requests_not_200:%s_%s" % (self.__provider, self.__api_key)
                self.msg_result = (-5, result_msg)
            else:
                self.answer_dict = web_data.json()

    def __answer_analyze_error(self):
        if self.__stop:
            return
        resp_code = int(self.answer_dict["code"])
        if resp_code == 40004:
            result_msg = "robot_call_num_over:%s_%s" % (self.__provider, self.__api_key)
            self.msg_result = (-2, result_msg)
        elif resp_code == 40007:
            result_msg = "robot_req_data_or_need:secret:%s_%s" % (self.__provider, self.__api_key)
            self.msg_result = (-1, result_msg)
        elif resp_code == 40002:
            result_msg = "robot_req_info_empty:%s_%s" % (self.__provider, self.__api_key)
            self.msg_result = (-3, result_msg)
        elif resp_code == 40001:
            result_msg = "robot_req_api_key_error:%s_%s" % (self.__provider, self.__api_key)
            self.msg_result = (-4, result_msg)

    def __answer_analyze_msg(self):
        if self.__stop:
            return
        html_a_tmpl = '<a href="{url}">{text}</a>'
        resp_code = int(self.answer_dict["code"])
        if resp_code == 100000: # 文本类
            self.answer_msg = self.answer_dict["text"]
        elif resp_code == 302000: # 新闻类
            self.answer_msg = self.answer_dict["text"] + "\n"
            for index, each in enumerate(self.answer_dict["list"][:self.__limit]):
                self.answer_msg += "\n"
                html_a_text = str(index+1) + "：" + each["article"]
                self.answer_msg += html_a_tmpl.format(url=each["detailurl"], text=html_a_text) + "\n"
        elif resp_code == 200000:
            self.answer_msg = html_a_tmpl.format(url=self.answer_dict["url"], text=self.answer_dict["text"])
        elif resp_code == 308000:  # 新闻类
            self.answer_msg = self.answer_dict["text"] + "\n"
            for index, each in enumerate(self.answer_dict["list"][:self.__limit]):
                self.answer_msg += "\n"
                html_a_text = str(index + 1) + "：" + each["name"]
                self.answer_msg += html_a_tmpl.format(url=each["detailurl"], text=html_a_text) + "\n"
                # self.answer_msg += each["info"]

    def __answer_analyze(self):
        self.__answer_analyze_error()
        self.__answer_analyze_msg()

    @property
    def __stop(self):
        if self.msg_result[0] < 0:
            return True

    def __clean(self):
        self.msg_result = (1, "get_msg_success")
        self.answer_dict = {}
        self.answer_msg = ""

    def get_answer(self, question, user_id=None):
        self.__clean()
        self.__requests(question, user_id)
        self.__answer_analyze()
        return self.answer_msg

