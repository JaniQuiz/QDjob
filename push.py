# push.py
import base64
import hashlib
import hmac
from datetime import datetime
import requests
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PushService(ABC):
    """推送服务基类"""

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self._validate_config()

    @abstractmethod
    def send(self, title: str, content: str) -> dict:
        """发送推送消息，返回包含成功状态的字典"""
        pass

    @abstractmethod
    def _validate_config(self):
        """验证配置有效性"""
        pass


class FeiShu(PushService):
    """飞书机器人推送"""

    def __init__(self, webhook_url: str, havesign: bool, secret: str = ""):
        self.havesign = havesign
        self.secret = secret
        self.webhook_url = webhook_url
        super().__init__()

    def _validate_config(self):
        """验证飞书配置"""
        # 验证webhook_url格式
        if not self.webhook_url.startswith(
            "https://open.feishu.cn/open-apis/bot/v2/hook/"
        ):
            logger.warning(
                f"[飞书配置] webhook_url 格式不推荐，建议使用飞书官方webhook地址"
            )

        # 验证签名配置
        if self.havesign and not isinstance(self.secret, str):
            logger.warning(
                f"[飞书配置] secret 必须为字符串类型，当前类型: {type(self.secret)}"
            )
            raise ValueError("secret 必须为字符串类型")

        # 验证签名配置
        if self.havesign and not self.secret:
            raise ValueError("启用签名校验必须提供secret")

    def gen_sign(self, timestamp: int) -> str:
        """生成签名"""
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(hmac_code).decode("utf-8")

    def creatcard(self, title: str, content: str) -> dict:
        """创建卡片消息"""
        return {
            "config": {"update_multi": True},
            "elements": [
                {
                    "tag": "markdown",
                    "content": content,
                    "text_align": "left",
                    "text_size": "normal",
                }
            ],
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue",
            },
        }

    def send(self, title: str, content: str) -> dict:
        """发送卡片消息"""
        try:
            timestamp = int(datetime.now().timestamp())
            card = self.creatcard(title, content)

            payload = {
                "msg_type": "interactive",
                "card": card,
            }

            if self.havesign:
                payload["sign"] = self.gen_sign(timestamp)
                payload["timestamp"] = timestamp

            response = requests.post(url=self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            success = result.get("code") == 0
            if not success:
                logger.debug(f"[飞书推送] 返回异常: {result}")

            return {"success": success, "raw": result, "service": "feishu"}

        except Exception as e:
            logger.error(f"[飞书推送] 发送异常: {str(e)}")
            return {"success": False, "error": str(e), "service": "feishu"}


class ServerChan(PushService):
    """Server酱推送"""

    def __init__(self, sckey: str):
        self.sckey = sckey
        super().__init__()

    def _validate_config(self):
        """验证Server酱配置"""
        if not self.sckey.startswith("SCU"):
            logger.warning(f"[Server酱配置] sckey 格式不推荐，建议使用标准格式")

    def send(self, title: str, content: str) -> dict:
        """发送文本消息"""
        try:
            url = f"https://sc.ftqq.com/{self.sckey}.send"
            data = {"text": title, "desp": content}

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()

            success = result.get("errno") == 0
            if not success:
                logger.debug(f"[Server酱] 返回异常: {result}")

            return {"success": success, "raw": result, "service": "serverchan"}

        except Exception as e:
            logger.error(f"[Server酱] 发送异常: {str(e)}")
            return {"success": False, "error": str(e), "service": "serverchan"}


# 新增推送服务只需继承PushService基类
class Telegram(PushService):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send(self, title: str, content: str) -> dict:
        # 实现Telegram推送逻辑
        pass


class Qiwei(PushService):
    """Qiwei推送"""

    def __init__(self, webhook_url: str, user_id: str):
        self.webhook_url = webhook_url
        self.user_id = user_id
        super().__init__()

    def _validate_config(self):
        """验证Qiwei配置"""
        if not self.webhook_url:
            logger.warning(f"[Qiwei配置] webhook_url 不能为空")

    def send(self, title: str, content: str) -> dict:
        """发送文本消息"""
        try:
            url = self.webhook_url
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f'## {title} \n { "<@"+ self.user_id +">" if self.user_id else ""}\n\n{content}',
                },
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()

            success = result.get("errcode") == 0

            if not success:
                logger.debug(f"[Qiwei企业微信] 返回异常: {result}")

            return {"success": success, "raw": result, "service": "qiwei"}

        except Exception as e:
            logger.error(f"[Qiwei企业微信] 发送异常: {str(e)}")
            return {"success": False, "error": str(e), "service": "qiwei"}
