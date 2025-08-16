from enum import Enum
import json, re
from utils import load_config, save_config, load_cookie, save_cookies

class ConfigKeys(Enum):
    DEFAULT_USER_AGENT = "default_user_agent"
    LOG_LEVEL = "log_level"
    LOG_RETENTION_DAYS = "log_retention_days"
    RETRY_ATTEMPTS = "retry_attempts"


class ConfigUsersKeys(Enum):
    USERNAME = "username"
    COOKIES_FILE = "cookies_file"
    USER_AGENT = "user_agent"
    SIGN_IN_TASK = "签到任务"
    INCENTIVE_FRAGMENT_TASK = "激励碎片任务"
    EXTRA_INCENTIVE_TASK = "额外激励任务"
    CHAPTER_CARD_TASK = "章节卡任务"
    DAILY_LOTTERY_TASK = "每日抽奖任务"

class ConfigUserCookieKeys(Enum):
    APP_ID = "appId"
    AREA_ID = "areaId"
    LANG = "lang"
    MODE = "mode"
    BAR = "bar"
    QIDTH = "qidth"
    QID = "qid"
    YWKEY = "ywkey"
    YWGUID = "ywguid"
    UUID = "uuid"
    CMFU_TOKEN = "cmfuToken"
    QDINFO = "QDInfo"


class ConfigUserCookie:
    def __init__(self, username, cookie_file):
        self._username = username
        self.cookie_file = cookie_file
        self._cookies = load_cookie(cookie_file)
    
    @property
    def cookies(self):
        return self._cookies
    
    @property
    def username(self):
        return self._username
    
    def _update(self, key: ConfigUserCookieKeys, value):
        if self._cookies is not None and self._verify(key, value):
            self._cookies[key.value] = value
            save_cookies(self.cookie_file, self._cookies)
    
    def _get(self, key: ConfigUserCookieKeys):
        return self._cookies.get(key.value) if self._cookies else None

    def _verify(self, key: ConfigUserCookieKeys, value):
        if key in [
            ConfigUserCookieKeys.APP_ID,
            ConfigUserCookieKeys.AREA_ID,
            ConfigUserCookieKeys.LANG,
            ConfigUserCookieKeys.MODE,
            ConfigUserCookieKeys.BAR,
            ConfigUserCookieKeys.QIDTH,
            ConfigUserCookieKeys.QID,
            ConfigUserCookieKeys.YWKEY,
            ConfigUserCookieKeys.YWGUID,
            ConfigUserCookieKeys.UUID,
            ConfigUserCookieKeys.CMFU_TOKEN,
            ConfigUserCookieKeys.QDINFO,
        ]:
            if not isinstance(value, str):
                raise ValueError(f"{key.value} - 必须是字符串")
            if not value:
                raise ValueError(f"{key.value} - 不能为空")
        return True
    
    def __getitem__(self, key):
        # 支持 ConfigUserCookieKeys 或 str
        if not isinstance(key, ConfigUserCookieKeys):
            key = ConfigUserCookieKeys(key)
        return self._get(key)

    def __setitem__(self, key, value):
        """设置属性值，自动校验值，校验失败报错

        Args:
            key (_type_): 键名，支持 ConfigKeys 或 str
            value (_type_): 键值
        """
        if not isinstance(key, Enum):
            key = ConfigUserCookieKeys(key)

        self._update(key, value)
    
    def updateFromStr(self, cookie_str: str):
        """根据字符串解析并更新Cookie信息

        Args:
            cookie_str (str): 以分号分隔的键值对字符串，必须包含ConfigUserCookieKeys列出的所有枚举值
        """
        
        cookies_dict = {}
        pairs = [p.strip() for p in cookie_str.split(";") if p.strip()]
            
        for pair in pairs:
            if "=" not in pair:
                raise ValueError(f"无效的键值对: {pair}")
                
            key, value = pair.split("=", 1)
            cookies_dict[key.strip()] = value.strip()
        
        # 遍历ConfigUserCookieKeys依次进行赋值
        missing_keys = []
        for key in ConfigUserCookieKeys:
            if key.value not in cookies_dict:
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"缺失的Cookie键: {', '.join(key.value for key in missing_keys)}")
        
        for key in ConfigUserCookieKeys:
            self[key] = cookies_dict[key.value]

    def isValid(self) -> bool:
        """判断Cookie配置信息是否有效
        
        目前粗浅判断各项是否已填
        
        Returns:
            bool: 是否有效
        """
        for key in ConfigUserCookieKeys:
            if not self[key]:
                return False
        return True

class ConfigUsers:
    def __init__(self, user_config):
        self._config = user_config
        
        # 获取到cookie对象，cookies_file为空会自动创建
        self.cookie = ConfigUserCookie(self.username, self._config.get("cookies_file", ""))

    @property
    def config(self):
        return self._config

    @property
    def username(self):
        return self._config.get("username")

    def _update(self, key: ConfigUsersKeys, value):
        if self._config is not None and self._verify(key, value):
            if key in [
                ConfigUsersKeys.USERNAME,
                ConfigUsersKeys.COOKIES_FILE,
                ConfigUsersKeys.USER_AGENT,
            ]:
                self._config[key.value] = value
            else:
                self.config["tasks"][key.value] = value
            ConfigManager()._update_user(self)

    def _get(self, key: ConfigUsersKeys):
        if key in [
            ConfigUsersKeys.USERNAME,
            ConfigUsersKeys.COOKIES_FILE,
            ConfigUsersKeys.USER_AGENT,
        ]:
            return self._config[key.value] if self._config else None
        else:
            return self.config["tasks"][key.value] if self._config else None

    def _verify(self, key: ConfigUsersKeys, value):
        if key in [
            ConfigUsersKeys.SIGN_IN_TASK,
            ConfigUsersKeys.INCENTIVE_FRAGMENT_TASK,
            ConfigUsersKeys.EXTRA_INCENTIVE_TASK,
            ConfigUsersKeys.CHAPTER_CARD_TASK,
            ConfigUsersKeys.DAILY_LOTTERY_TASK,
        ]:
            if not isinstance(value, bool):
                raise ValueError(f"{key} - 任务配置必须是布尔值")
        elif key == ConfigUsersKeys.COOKIES_FILE:
            if not isinstance(value, str) or not value.endswith(".json") or not value.startswith("cookies/"):
                raise ValueError(f"{key} - 必须是以 'cookies/' 开头并且以 '.json' 结尾的字符串")
            # 更新cookie对象
            self.cookie = ConfigUserCookie(self.username, value)
        elif key == ConfigUsersKeys.USER_AGENT:
            if value != "":
                match = re.search(
                    r"Android (\d+); ([^;]+) Build/.*?QDReaderAndroid/(\d+\.\d+\.\d+)/(\d+)/(\d+)/([^/]+)/",
                    value,
                )
                if not match or any(not match.group(i) for i in range(1, 7)):
                    raise ValueError(
                        "无法从User-Agent中正确获取信息，请检查User-Agent是否正确"
                    )
        else:
            if not isinstance(value, str):
                raise ValueError(f"{key} - 必须是字符串")

        return True

    def __getitem__(self, key):
        # 支持 ConfigUsersKeys 或 str
        if not isinstance(key, ConfigUsersKeys):
            key = ConfigUsersKeys(key)
        return self._get(key)

    def __setitem__(self, key, value):
        """设置属性值，自动校验值，校验失败报错

        Args:
            key (_type_): 键名，支持 ConfigKeys 或 str
            value (_type_): 键值
        """
        if not isinstance(key, Enum):
            key = ConfigUsersKeys(key)

        self._update(key, value)


class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def config(self):
        if self._config is None:
            self._config = load_config()
        return self._config

    def _update(self, key: ConfigKeys, value):
        if self.config is not None and self._verify(key, value):
            self._config[key.value] = value
            save_config(self._config)

    def _update_user(self, user: ConfigUsers):
        username = user.username
        value = user.config

        for index, user in enumerate(self._config.get("users", [])):
            if user.get("username") == username:
                self._config["users"][index] = value
                save_config(self._config)
                return

        # 查找失败
        raise KeyError(f"用户 {username} 不存在")

    def _get(self, key: ConfigKeys):
        return self._config[key.value] if self._config else None

    def _verify(self, key: ConfigKeys, value):
        """校验配置项值

        Args:
            key (ConfigKeys): 配置项键 ConfigKeys 枚举值
            value (_type_): 配置项值
        """
        if key == ConfigKeys.DEFAULT_USER_AGENT:
            match = re.search(
                r"Android (\d+); ([^;]+) Build/.*?QDReaderAndroid/(\d+\.\d+\.\d+)/(\d+)/(\d+)/([^/]+)/",
                value,
            )
            if not match or any(not match.group(i) for i in range(1, 7)):
                raise ValueError(
                    "'无法从User-Agent中正确获取信息，请检查User-Agent是否正确'"
                )
        elif key == ConfigKeys.LOG_LEVEL:
            if value not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                raise ValueError(f"无效的日志级别: {value}")
        elif key == ConfigKeys.LOG_RETENTION_DAYS:
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"无效的日志保留天数: {value}")
        elif key == ConfigKeys.RETRY_ATTEMPTS:
            if not isinstance(value, int) or value < 0 or value > 10:
                raise ValueError(f"无效的重试次数: {value}, 必须是0到10之间的整数")
        else:
            raise KeyError(f"未知的配置项: {key}")

        return True

    def __getitem__(self, key):
        # 支持 ConfigKeys 或 str
        k = key.value if isinstance(key, Enum) else key
        return self.config.get(k)

    def __setitem__(self, key, value):
        """设置属性值，自动校验值，校验失败报错

        Args:
            key (_type_): 键名，支持 ConfigKeys 或 str
            value (_type_): 键值
        """
        if not isinstance(key, Enum):
            key = ConfigKeys(key)

        self._update(key, value)
    
    def listUsername(self):
        return [user.get("username") for user in self.config.get("users", [])]

    def getUser(self, username: str):
        for user in self.config.get("users", []):
            if user.get("username") == username:
                return ConfigUsers(user)
        return None

    def addUser(self, username: str):
        cookie_file = f"cookies/{re.sub(r'[\\/:*?\"<>|]', '_', username)}.json"
        user = ConfigUsers(
            {
                "username": username,
                "cookies_file": cookie_file,
                "user_agent": "",
                "tasks": {
                    "签到任务": True,
                    "激励碎片任务": True,
                    "额外激励任务": True,
                    "章节卡任务": True,
                    "每日抽奖任务": True,
                },
                "push_services": [],
            }
        )
        self.config["users"].append(user.config)
        return user
    
    def removeUser(self, username: str):
        for index, user in enumerate(self.config.get("users", [])):
            if user.get("username") == username:
                del self.config["users"][index]
                save_config(self.config)
                return
        raise KeyError(f"用户 {username} 不存在")

config = ConfigManager()