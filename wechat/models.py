import os

from django.db import models

# Create your models here.
from smallsite import settings
from wechat.settings import WECHAT_MENU_TYPE_CHOICE, SERVER_STATUS, \
    WECHAT_ENCRYPT_MODE_CHOICE, IS_DISPLAY_CHOICE, IS_ONLINE_CHOICE, \
    WECHAT_MESSAGE_TYPE, WECHAT_SEND_MESSAGE_TYPE, PRIORITY_CHOICE, \
    ROBOT_PROVIDER_CHOICE, WECHAT_ALL_MSG_TYPE


class WechatDetail(models.Model):
    name = models.CharField("名称", max_length=36, help_text="[未]")
    status = models.SmallIntegerField("状态", default=0,
                                      choices=SERVER_STATUS)
    is_auth = models.BooleanField("是否认证", default=False)
    original_id = models.CharField("原始ID", max_length=15, unique=True,
                                   help_text="由15位字符组成")
    app_id = models.CharField("应用ID", max_length=18,
                              help_text="由18位字符组成")
    url = models.CharField("服务器地址", max_length=255)
    app_secret = models.CharField("应用密钥", max_length=32,
                                  help_text="由32位字符组成")
    token = models.CharField("令牌", max_length=32, help_text="由32位字符组成")
    encoding_aes_key = models.CharField("消息加密密钥", max_length=43,
                                        blank=True, default="",
                                        help_text="由43位字符组成")
    encrypt_mode = models.CharField(
        "消息加解密方式", max_length=36, default="safe",
        choices=WECHAT_ENCRYPT_MODE_CHOICE,
        help_text="<p>明文模式下，不使用消息体加解密功能，安全系数较低</p>"
                  "<p>兼容模式下，明文、密文将共存，方便开发者调试和维护</p>"
                  "<p>安全模式下，消息包为纯密文，需要开发者加密和解密，安全系数高</p>")
    remark = models.CharField("备注", max_length=255, blank=True, default="",
                              help_text="[未]")
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_detail"
        verbose_name = "微信详情配置"
        verbose_name_plural = "微信详情配置"

    def get_core(self):
        return {
            "appid": self.app_id,
            "appsecret": self.app_secret,
            "token": self.token,
            "encrypt_mode": self.encrypt_mode,
            "encoding_aes_key": self.encoding_aes_key,
        }

    def get_all(self):
        data = self.get_core()
        data.update({
            "name": self.name,
            "status": self.status,
            "is_auth": self.is_auth,
            "url": self.url,
            "original_id": self.original_id,

        })
        return data

    def __str__(self):
        return self.name


class WechatMenuSubConfig(models.Model):
    wm_title = models.CharField(
        "标题", max_length=36,
        help_text="一级菜单最多4个汉字，二级菜单最多7个汉字，多出来的部分将会以“...”代替。")
    wm_type = models.CharField(
        "菜单类型", max_length=36, choices=WECHAT_MENU_TYPE_CHOICE, blank=True,
        default="",
        help_text='<a href="https://mp.weixin.qq.com/wiki" target="_blank">详细介绍</a>')
    wm_pos = models.SmallIntegerField(
        "位置", default=1,
        help_text="自定义菜单最多包括3个一级菜单，每个一级菜单最多包含5个二级菜单，数字：1-5")
    wm_key = models.CharField(
        "key | url | media_id", max_length=255, blank=True, default="")
    is_display = models.BooleanField("是否可选", default=True,
                                     choices=IS_DISPLAY_CHOICE)
    remark = models.CharField("备注", max_length=255, blank=True, default="",
                              help_text="[未]")
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_sub_menu"
        verbose_name = "微信菜单子配置"
        verbose_name_plural = "微信菜单子配置"

    def __str__(self):
        return "{title}-{type}-位置:{pos}".format(
            title=self.wm_title, pos=self.wm_pos,
            type=dict(WECHAT_MENU_TYPE_CHOICE)[self.wm_type])


class WechatMenuConfig(models.Model):
    level_1 = models.ForeignKey(WechatMenuSubConfig, related_name="select_menu",
                                verbose_name="一级菜单",
                                limit_choices_to={"is_display": True})
    level_2 = models.ManyToManyField(WechatMenuSubConfig, blank=True,
                                     related_name="select_menus",
                                     default=None, verbose_name="耳机菜单")
    is_online = models.BooleanField("是否上线", default=True,
                                    choices=IS_ONLINE_CHOICE)
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_menu"
        verbose_name = "微信菜单配置"
        verbose_name_plural = "微信菜单配置"

SEX_CHOICE = (
    (0, "未知"),
    (1, "男性"),
    (2, "女性"),
)

class WechatUser(models.Model):
    is_subscribe = models.BooleanField("是否订阅", default=True)
    openid = models.CharField("OpenID", max_length=36, unique=True)
    nickname = models.CharField("昵称", max_length=36)
    sex = models.SmallIntegerField("性别", choices=SEX_CHOICE)
    city = models.CharField("城市", max_length=36)
    country = models.CharField("国家", max_length=36)
    province = models.CharField("省份", max_length=36)
    language = models.CharField("语言", max_length=36)
    headimgurl = models.CharField("用户头像", max_length=255)
    subscribe_time = models.CharField("关注时间", max_length=16)
    unionid = models.CharField("UnionID", max_length=16, blank=True, default="")
    remark = models.CharField("备注名称", max_length=16, blank=True, default="")
    group_id = models.IntegerField("GroupID")
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_user"
        verbose_name = "微信用户"
        verbose_name_plural = "微信用户"

    def __str__(self):
        return "%s-%s" % (self.nickname, self.openid)

class WechatMessageLog(models.Model):
    wx_user = models.ForeignKey(WechatUser, default=None,
                                verbose_name="微信用户")
    msg_type = models.CharField("消息类型", choices=WECHAT_MESSAGE_TYPE,
                                default="text", max_length=36)
    msg = models.TextField("消息数据", blank=True, default="")
    msg_file = models.FileField("消息文件", blank=True, default="",
                                upload_to="private/wechat/msg_file/msg/")
    is_replied = models.BooleanField("是否已回复", default=False)
    reply_msg = models.TextField("回复内容", blank=True, default="")
    reply_file = models.FileField("回复文件", blank=True, default="",
                                  upload_to="private/wechat/msg_file/reply/")
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_message_log"
        verbose_name = "微信消息"
        verbose_name_plural = "微信消息"

    def get_msg_file_url(self):
        return settings.SITE_HOST + self.msg_file.url

    # def save(self, *args, **kwargs):
    #
    #     super(WechatMessage, self).save(*args, **kwargs)


class WechatAutoReply(models.Model):
    name = models.CharField("名称", max_length=36, help_text="[未]仅助记")
    msg_type = models.CharField("消息类型", choices=WECHAT_ALL_MSG_TYPE,
                                default="text", max_length=36)
    priority = models.SmallIntegerField(
        "优先级", default=0, choices=PRIORITY_CHOICE,
        help_text="所有【事件消息】将忽略优先级配置")
    keyword = models.CharField(
        "关键字", max_length=255, blank=True, default="",
        help_text="<p style='font-weight:bold;'>普通消息：</p>"
                  "<p>&nbsp;&nbsp;多个以【|】分割，英文不区分大小写，可不填</p>"
                  "<p>&nbsp;&nbsp;不填，将匹配任何消息，如无特殊需求请保持此配"
                  "置【优先级】【最低】，如【消息类型】为【文本消息】此配置将使"
                  "机器人回复失效</p>"
                  "<p style='font-weight:bold;'>事件消息：</p>"
                  "<p>&nbsp;&nbsp;此处需要对应填写，多个以【|】分割，可不填"
                  "<p>&nbsp;&nbsp;点击事件：对应的key</p>"
                  "<p>&nbsp;&nbsp;其他事件：请留【空】</p>"
    )
    reply_msg = models.TextField(
        "回复内容",
        help_text="<p>没有具体要求，可以使用a标签</p>"
                  "<p style='font-weight:bold;'>动态关键词：</p>"
                  "<p>目前支持部分动态关键词，可在对应事件中添加：</p>"
                  "<p>&nbsp;&nbsp;关注事件：昵称{nickname}</p>")
    reply_file = models.FileField("回复文件", blank=True, default="",
                                  upload_to="private/wechat/msg_file/reply/")
    is_online = models.BooleanField("是否上线", default=True,
                                    choices=IS_ONLINE_CHOICE)
    is_valid = models.BooleanField("是否生效", default=False)
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "wechat_auto_reply"
        verbose_name = "微信自动回复"
        verbose_name_plural = "微信自动回复"

    def save(self, *args, **kwargs):
        self.is_valid = kwargs.pop("is_valid", False)
        self.keyword = self.keyword.strip().strip("|").lower()
        super(WechatAutoReply, self).save(*args, **kwargs)


class RobotDetail(models.Model):
    provider = models.CharField("提供商", choices=ROBOT_PROVIDER_CHOICE,
                                default="tuling", max_length=36)
    name = models.CharField("机器人名称", max_length=36)
    status = models.SmallIntegerField("状态", default=0,
                                      choices=SERVER_STATUS)
    priority = models.SmallIntegerField(
        "优先级", default=0, choices=PRIORITY_CHOICE)
    call_num = models.PositiveSmallIntegerField("调用次数", default=5000)
    api_key = models.CharField("APIkey", max_length=36)
    is_secret = models.BooleanField("是否加密", default=False,
                                    help_text="暂时不支持")
    secret = models.CharField("加密secret", max_length=36, default="",
                              blank=True)
    ctime = models.DateTimeField("创建时间", auto_now_add=True)
    utime = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "robot_detail"
        verbose_name = "机器人详情"
        verbose_name_plural = "机器人详情"

    def save(self, *args, **kwargs):
        self.api_key = self.api_key.strip()
        self.secret = self.secret.strip()
        super(RobotDetail, self).save(*args, **kwargs)