from enum import Enum


class GlobalVariables:
    """
    单实例类，保存全局变量
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 避免重复初始化
        pass


class AppBarStatus(Enum):
    MAIN = "main"
    EDIT = "edit"
    SETTINGS = "settings"
    CONFIG_DETAIL = "config_detail"
    CONFIG_EDIT = "config_edit"


app = GlobalVariables()
