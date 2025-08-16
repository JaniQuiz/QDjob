import os, json

FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")

if FLET_APP_STORAGE_DATA is None:
    # 测试情况
    FLET_APP_STORAGE_DATA = "./storage/data"

CONFIG_PATH = os.path.join(FLET_APP_STORAGE_DATA, "config.json")


def load_config():
    """加载或初始化配置文件"""
    if not os.path.exists(CONFIG_PATH):
        # 创建默认配置
        default_config = {
            "default_user_agent": "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading",
            "log_level": "INFO",
            "log_retention_days": 7,
            "retry_attempts": 3,
            "users": [],
        }
        save_config(default_config)
        os.makedirs("cookies", exist_ok=True)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_cookie(cookie_file):
    """加载Cookie文件"""
    cookie_path = os.path.join(FLET_APP_STORAGE_DATA, cookie_file)
    if not os.path.exists(cookie_path):
        # 创建默认配置
        default_cookies = {
            "appId": "",
            "areaId": "",
            "lang": "",
            "mode": "",
            "bar": "",
            "qidth": "",
            "qid": "",
            "ywkey": "",
            "ywguid": "",
            "uuid": "",
            "cmfuToken": "",
            "QDInfo": "",
        }
        save_cookies(cookie_file, default_cookies)
    with open(cookie_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cookies(cookie_file, cookies):
    """保存Cookie文件"""
    cookie_path = os.path.join(FLET_APP_STORAGE_DATA, cookie_file)
    with open(cookie_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
