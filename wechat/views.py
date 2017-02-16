import logging

from django.http import HttpResponse
from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
# Create your views here.
from wechat_sdk.messages import TextMessage

from smallsite import settings
from wechat.mixin import MessageHandleMixin
from wechat.models import WechatUser

logger = logging.getLogger("default")


class TokenCheckView(View):
    # hfXe1iREB8vU3pJFz4Ed0WHNXMXB7dcLhpusEj6Abic
    # f4440f46565a12a04921b4b8b9ab85d9
    # http: // www.smallsite.cn / wechat /
    def dispatch(self, request, *args, **kwargs):
        signature = self.request.GET["signature"]
        timestamp = self.request.GET.get("timestamp")
        nonce = self.request.GET.get("nonce")
        echostr = self.request.GET.get("echostr")
        logger.info("wechat_token_check", extra={"signature": signature,
                                                  "timestamp": timestamp,
                                                  "nonce": nonce,
                                                  "echostr": echostr})
        return HttpResponse(echostr)

class MessageView(MessageHandleMixin, View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        # 避免跨域请求权限不足直接403错误
        return super(MessageView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        signature = self.request.GET["signature"]
        timestamp = self.request.GET["timestamp"]
        nonce = self.request.GET["nonce"]
        echo_str = self.request.GET["echostr"]

        logger.info("wechat_get", extra={"signature": signature,
                                         "timestamp": timestamp,
                                         "nonce": nonce})
        result = self.wechat.check_signature(signature, timestamp, nonce)
        logger.info("wechat_token_check", extra={"signature": signature,
                                                 "timestamp": timestamp,
                                                 "nonce": nonce,
                                                 "result": result})
        if result:
            return HttpResponse(echo_str, content_type="text/plain")
        else:
            return HttpResponse('none', content_type="text/plain")

    def post(self, *args, **kwargs):
        # 对签名进行校验
        signature = self.request.GET["signature"]
        timestamp = self.request.GET["timestamp"]
        nonce = self.request.GET["nonce"]
        openid = self.request.GET["openid"]
        if not settings.DEBUG and not self.wechat.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseNotFound()
        # if not WechatUser.objects.filter(openid=openid).exists():
        #     self.save_user_info(openid)
        # 对 XML 数据进行解析 (必要, 否则不可执行 response_text, response_image 等操作)
        # TODO: 之后要改成加解密传输
        self.wechat.parse_data(self.request.body)
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = self.wechat.get_message()
        extra_log = {"raw": message.raw,
                     "url": self.request.path,
                     "message_type": message.type,
                     "query_params": self.request.GET,
                     "openid": message.source,
                     "ctime": message.time
                     }
        if isinstance(message, TextMessage):
            extra_log.update({"content": message.content})
        logger.info("WECHAT_MESSAGE", extra=extra_log)
        try:
            response = self.msg_handle(message)
        except:
            import traceback
            errors = traceback.format_exc()
            logger.error("wechat_msg_handle",
                         extra={"error": errors})
            return
        return HttpResponse(response, content_type="application/xml")

