import json
import logging
import time
from io import BytesIO
from django.contrib import admin
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
# Register your models here.
from utils.admin_mixin import CustomAdmin
from utils.tools import redis_ins, try_except_log
from wechat.forms import WechatMenuConfigAdminForm
from wechat.models import WechatDetail, WechatMenuSubConfig, WechatMenuConfig, \
    WechatUser, WechatMessageLog, WechatAutoReply, RobotDetail
from wechat.settings import WECHAT_CONFIG_KEYS, WECHAT_AUTO_REPLY_KEY, \
    WECHAT_MESSAGE_TYPE_RELATED, WECHAT_EVENT_TYPE_RELATED
from wechat.tools import GetWechat, SetWechat, get_media_type

logger = logging.getLogger("default")


class WechatDetailAdmin(admin.ModelAdmin):
    list_display = ("name", "original_id", "status", "is_auth", "expires_at",
                    "ctime", "utime", "remark", "access_token")
    list_editable = ("status", )
    actions = ("refresh_access_token", )
    list_per_page = 20

    def refresh_access_token(self, request, queryset):
        for obj in queryset:
            GetWechat.refresh_config_redis(obj.original_id)
        messages.success(request, "共 %s条 刷新完成" % queryset.count())

    refresh_access_token.short_description = "刷新access_token"

    def access_token(self, obj):
        redis_app_id = redis_ins.hget(WECHAT_CONFIG_KEYS, "app_id")
        if redis_app_id and obj.app_id == redis_app_id:
            return redis_ins.hget(WECHAT_CONFIG_KEYS, "access_token")
        return "-"

    access_token.short_description = "Access Token"

    def expires_at(self, obj):
        redis_app_id = redis_ins.hget(WECHAT_CONFIG_KEYS, "app_id")
        if redis_app_id and obj.app_id == redis_app_id:
            expires_timestamp = int(redis_ins.hget(WECHAT_CONFIG_KEYS,
                                                   "access_token_expires_at"))
            time_local = time.localtime(expires_timestamp)
            return time.strftime('%Y-%m-%d %H:%M:%S', time_local)
        return "-"

    expires_at.short_description = "Expires At"

admin.site.register(WechatDetail, WechatDetailAdmin)


class WechatMenuSubConfigAdmin(admin.ModelAdmin):
    list_display = ("wm_title", "wm_type", "wm_pos", "is_display", "wm_key",
                    "remark", "ctime", "utime")
    list_filter = ("is_display", )
    list_per_page = 20

admin.site.register(WechatMenuSubConfig, WechatMenuSubConfigAdmin)


class WechatMenuConfigAdmin(CustomAdmin):
    list_display = ("l_1", "l_2s", "pos", "is_online", "ctime", "utime")
    list_filter = ("is_online", )
    list_per_page = 20
    form = WechatMenuConfigAdminForm
    actions = ("update_menu", "get_menu", "delete_menu")
    list_editable = ("is_online", )

    def l_1(self, obj):
        return obj.level_1.wm_title

    l_1.short_description = "一级标题"

    def pos(self, obj):
        return obj.level_1.wm_pos

    pos.short_description = "一级位置"

    def l_2s(self, obj):
        if not obj.level_2:
            return "-"
        titles = obj.level_2.values_list("wm_title", flat=True)
        return "<p>%s</p>" % ("</p><p>".join(titles))

    l_2s.short_description = "二级菜单"
    l_2s.allow_tags = True

    def update_menu(self, request, queryset):
        if WechatMenuConfig.objects.filter(is_online=True).exists():
            wx_msg = SetWechat().menu()
        else:
            wx_msg = SetWechat().delete_menu()
        messages.success(request, wx_msg)

    update_menu.short_description = "更新菜单"
    update_menu.no_select_action = True

    def delete_menu(self, request, queryset):
        messages.success(request, SetWechat().delete_menu())

    delete_menu.short_description = "删除菜单"
    delete_menu.no_select_action = True

    def get_menu(self, request, queryset):
        messages.success(request, GetWechat().menu)

    get_menu.short_description = "获取菜单"
    get_menu.no_select_action = True

admin.site.register(WechatMenuConfig, WechatMenuConfigAdmin)


class WechatUserAdmin(admin.ModelAdmin):
    list_display = ("nickname_display", "is_subscribe", "openid", "sex", "city",
                    "group_id", "ctime", "utime")
    list_per_page = 20
    search_fields = ("nickname", "=openid")
    list_filter = ("ctime", "is_subscribe", "group_id")

    def nickname_display(self, obj):
        if obj.nickname:
            return obj.nickname
        return obj.openid

    nickname_display.short_description = "昵称"

admin.site.register(WechatUser, WechatUserAdmin)


class WechatMessageLogAdmin(CustomAdmin):
    list_display = ("nickname", "is_subscribe", "is_replied", "msg_type",
                    "msg_file_click", "msg_brief", "reply_msg_brief",
                    "reply_file_click", "openid", "ctime", "utime")
    list_filter = ("msg_type", "is_replied","ctime")
    list_per_page = 20
    raw_id_fields = ("wx_user", )
    actions = ("send_msg", "download_media")
    search_fields = ("=wx_user__openid", )
    # formfield_overrides = {models.CharField: {'widget': forms.Textarea},}

    def nickname(self, obj):
        if obj.wx_user.nickname:
            return obj.wx_user.nickname
        return obj.wx_user.openid

    nickname.short_description = "昵称"

    def openid(self, obj):
        return obj.wx_user.openid

    openid.short_description = "OpenID"

    def is_subscribe(self, obj):
        html_true = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
        html_false = '<img src="/static/admin/img/icon-no.svg" alt="False">'
        return html_true if obj.wx_user.is_subscribe else html_false
        # return "是" if obj.wx_user.subscribe else "否"

    is_subscribe.short_description = "是否订阅"
    is_subscribe.allow_tags = True

    def msg_file_click(self, obj):
        if obj.msg_file:
            return '<a target="_blank" href="{0}"> {1} </a>'.format(
                obj.msg_file.url, "点击查看")
        return "-"

    msg_file_click.short_description = "消息文件"
    msg_file_click.allow_tags = True

    def msg_brief(self, obj):
        if obj.msg_type == "text":
            msg = eval(obj.msg)["content"]
        else:
            msg = obj.msg
        if msg and len(msg)>20:
            return msg[:20] + "... ..."
        else:
            return msg if msg else "-"

    msg_brief.short_description = "消息内容"

    def reply_msg_brief(self, obj):
        if obj.reply_msg and len(obj.reply_msg) > 20:
            return obj.reply_msg[:20] + "... ..."
        else:
            return obj.reply_msg if obj.reply_msg else "-"

    reply_msg_brief.short_description = "回复内容"

    def reply_file_click(self, obj):
        if obj.reply_file:
            return '<a target="_blank" href="{0}"> {1} </a>'.format(
                obj.reply_file.url, "点击查看")
        return "-"

    reply_file_click.short_description = u"回复文件"
    reply_file_click.allow_tags = True

    def send_msg(self, request, queryset):
        error_count = 0
        total_count = 0
        filter_queryset = queryset.filter(is_replied=False)
        for obj in filter_queryset:
            total_count += 1
            if not obj.reply_msg and not obj.reply_file:
                error_count += 1
                continue
            try:
                if obj.reply_msg:
                    GetWechat().wechat_obj.send_text_message(
                        obj.wx_user.openid, obj.reply_msg)
                if obj.reply_file:
                    media_type = get_media_type(obj.reply_file.path)
                    with open(obj.reply_file.path, "rb") as fd:
                        resq = GetWechat().wechat_obj.upload_media(media_type, fd)
                    # GetWechat().wechat_obj.send_video_message()
                obj.is_replied = True
                obj.save()
            except:
                import traceback
                errors = traceback.format_exc()
                logger.error("wechat_send_msg_error", extra={"error": errors})
                error_count += 1
        messages.success(request,
                         "共 %s 条，失败 %s 条" % (total_count, error_count))

    send_msg.short_description = "发送消息"
    send_msg.all_select_action = True

    @try_except_log
    def download_media(self, request, queryset):
        filter_queryset = queryset.exclude(
            msg_type__in=["text", "link", "location", "other"]).filter(msg_file="")
        for obj in filter_queryset:
            msg_dict = eval(obj.msg)
            media_id = msg_dict["media_id"]
            response = GetWechat().wechat_obj.download_media(media_id)
            find_file_name = response.headers["content-disposition"]
            file_name_start = find_file_name.find("filename=") + len("filename=")
            file_name = find_file_name[file_name_start:]
            file_type = response.headers["content-type"]
            buffer = BytesIO()
            for chunk in response.iter_content(1024):
                buffer.write(chunk)
            filebuffer = InMemoryUploadedFile(
                buffer, None, file_name, file_type, len(buffer.getvalue()), None)
            obj.msg_file.save(file_name, filebuffer)
            messages.success(request, "拉取完成")

    download_media.short_description = "下载媒体文件"

admin.site.register(WechatMessageLog, WechatMessageLogAdmin)


class WechatAutoReplyAdmin(CustomAdmin):
    list_display = ("name", "is_online_display", "is_valid", "priority",
                    "keyword_display", "msg_type", "reply_msg_brief",
                    "reply_file_click", "ctime", "utime")
    list_per_page = 20
    list_filter = ("msg_type", )
    exclude = ("is_valid", )
    actions = ("update_redis_auto_reply", )

    def is_online_display(self, obj):
        html_true = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
        html_false = '<img src="/static/admin/img/icon-no.svg" alt="False">'
        return html_true if obj.is_online else html_false

    is_online_display.short_description = "是否上线"
    is_online_display.allow_tags = True

    def keyword_display(self, obj):
        if obj.keyword and len(obj.keyword) > 20:
            return obj.reply_msg[:20] + "... ..."
        else:
            return obj.keyword if obj.keyword else "-"
    keyword_display.short_description = "关键字"

    def reply_msg_brief(self, obj):
        if obj.reply_msg and len(obj.reply_msg) > 20:
            return obj.reply_msg[:20] + "... ..."
        else:
            return obj.reply_msg if obj.reply_msg else "-"

    reply_msg_brief.short_description = "回复内容"

    def reply_file_click(self, obj):
        if obj.reply_file:
            return '<a target="_blank" href="{0}"> {1} </a>'.format(
                obj.reply_file.url, "点击查看")
        return "-"

    reply_file_click.short_description = "回复文件"
    reply_file_click.allow_tags = True

    def update_redis_auto_reply(self, request, queryset):
        all_query = WechatAutoReply.objects.filter(is_online=True)
        event_msg_types = WECHAT_EVENT_TYPE_RELATED.keys()
        event_msg_query = all_query.filter(msg_type__in=event_msg_types)
        general_msg_types = WECHAT_MESSAGE_TYPE_RELATED.keys()
        general_msg_query = all_query.filter(msg_type__in=general_msg_types)
        for msg_type in general_msg_types:
            redis_key = WECHAT_AUTO_REPLY_KEY + msg_type
            redis_ins.delete(redis_key)
            reply_pri_msg_dict = {}
            for obj in general_msg_query.filter(msg_type=msg_type):
                keywords = obj.keyword.split("|")
                reply_pri_msg_dict.setdefault(obj.priority, {})
                for keyword in keywords:
                    reply_pri_msg_dict[obj.priority].update(
                        {keyword: obj.reply_msg})
            for pri, msg_dict in reply_pri_msg_dict.items():
                redis_ins.zadd(redis_key, json.dumps(msg_dict), pri)

        redis_key = WECHAT_AUTO_REPLY_KEY + "event"
        redis_ins.delete(redis_key)
        for msg_type in event_msg_types:
            reply_msg_dict = {}
            for obj in event_msg_query.filter(msg_type=msg_type):
                keywords = obj.keyword.split("|")
                for keyword in keywords:
                    reply_msg_dict.update({keyword: obj.reply_msg})
                redis_ins.hset(redis_key, obj.msg_type,
                               json.dumps(reply_msg_dict))

        WechatAutoReply.objects.update(is_valid=True)
        messages.success(request,
                         "共 %s 条 已全部刷新完成" % WechatAutoReply.objects.count())

    update_redis_auto_reply.short_description = "强制刷新全部配置"
    update_redis_auto_reply.no_select_action = True

admin.site.register(WechatAutoReply, WechatAutoReplyAdmin)


class RobotDetailAdmin(admin.ModelAdmin):
    list_display = ("provider", "name", "status", "priority", "call_num",
                    "api_key", "is_secret", "secret", "ctime", "utime")
    list_per_page = 20

admin.site.register(RobotDetail, RobotDetailAdmin)




