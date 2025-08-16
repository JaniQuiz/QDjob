import flet as ft
from components import AboutCard
from config import config, ConfigKeys
from globalApp import app, AppBarStatus



class SettingsView(ft.Column):
    def __init__(self):
        super().__init__()

        print("SettingsView init")

        self.defaultUserAgentEdit = ft.TextField(
            label="默认用户代理",
            multiline=True,
            min_lines=3,
            max_lines=10,
            hint_text=f"请输入默认用户代理",
            value=config[ConfigKeys.DEFAULT_USER_AGENT],
            expand=True,
        )

        def reset_default_user_agent(e):
            self.defaultUserAgentEdit.value = "Mozilla/5.0 (Linux; Android 15; V2171A Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/137.0.7151.115 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.417/1636/1000009/vivo/QDShowNativeLoading"
            self.defaultUserAgentEdit.update()
            
        self.resetButton = ft.FilledButton(
            "恢复默认",
            icon=ft.Icons.REPLAY,
            on_click=reset_default_user_agent,  # 直接传递函数引用
        )

        logLevelOptions = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        dropdownOptions = []

        for item in logLevelOptions:
            dropdownOptions.append(
                ft.DropdownOption(key=item, content=ft.Text(value=item))
            )

        self.logLevelDropdown = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            label="日志等级",
            options=dropdownOptions,
            value=config[ConfigKeys.LOG_LEVEL],
            expand=True,
        )

        self.logRetentionDaysEdit = ft.TextField(
            label="日志保存天数",
            hint_text="请输入日志保存天数 大于0",
            value=str(config[ConfigKeys.LOG_RETENTION_DAYS]),
            keyboard_type=ft.KeyboardType.NUMBER,
            suffix_text="天",
            expand=True,
        )

        self.retryAttemptsEdit = ft.TextField(
            label="任务重试次数",
            hint_text="请输入任务重试次数 0-10",
            value=str(config[ConfigKeys.RETRY_ATTEMPTS]),
            keyboard_type=ft.KeyboardType.NUMBER,
            suffix_text="次",
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("DefaultUser Agent 默认用户代理"),
                        ft.Text(
                            " 开始末尾不要有空格和空行 ",
                            size=12,
                        ),
                    ]
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                expand=True,  # 横向拉满
                padding=10,  # 可选：让内容不贴边
            ),
            ft.Row(controls=[self.defaultUserAgentEdit, self.resetButton]),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("日志等级"),
                        ft.Text(
                            " DEBUG -> CRITICAL 输出内容依次减少 ",
                            size=12,
                        ),
                    ]
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                expand=True,  # 横向拉满
                padding=10,  # 可选：让内容不贴边
            ),
            self.logLevelDropdown,
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("日志保存时间"),
                        ft.Text(
                            " 可选择保留日志 1-30 天 ",
                            size=12,
                        ),
                    ]
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                expand=True,  # 横向拉满
                padding=10,  # 可选：让内容不贴边
            ),
            self.logRetentionDaysEdit,
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("任务重试次数"),
                        ft.Text(
                            " 可选择任务失败后重试次数 0-10 次 0为失败不重试 ",
                            size=12,
                        ),
                    ]
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                expand=True,  # 横向拉满
                padding=10,  # 可选：让内容不贴边
            ),
            self.retryAttemptsEdit,
            AboutCard(),
        ]

        self.scroll = ft.ScrollMode.HIDDEN  # 超出自动滚动但不显示滚动条

    def update_value(self):
        self.defaultUserAgentEdit.value = config[ConfigKeys.DEFAULT_USER_AGENT]
        self.defaultUserAgentEdit.update()
        self.logLevelDropdown.value = config[ConfigKeys.LOG_LEVEL]
        self.logLevelDropdown.update()
        self.logRetentionDaysEdit.value = config[ConfigKeys.LOG_RETENTION_DAYS]
        self.logRetentionDaysEdit.update()
        self.retryAttemptsEdit.value = config[ConfigKeys.RETRY_ATTEMPTS]
        self.retryAttemptsEdit.update()

    def on_switch(self):
        app.appBar.change_bar(AppBarStatus.SETTINGS)
        self.update_value()

    def save(self):
        print("保存设置")
        try:
            config[ConfigKeys.DEFAULT_USER_AGENT] = self.defaultUserAgentEdit.value
            config[ConfigKeys.LOG_LEVEL] = self.logLevelDropdown.value
            config[ConfigKeys.LOG_RETENTION_DAYS] = int(self.logRetentionDaysEdit.value)
            config[ConfigKeys.RETRY_ATTEMPTS] = int(self.retryAttemptsEdit.value)
            
            dlg = ft.AlertDialog(
                title=ft.Text("操作成功"),
                content=ft.Text("设置项已成功保存"),
                title_padding=ft.padding.all(15),
            )

            app.page.open(dlg)
        except Exception as e:
            dlg = ft.AlertDialog(
                title=ft.Text("设置项出错"),
                content=ft.Text(f"报错内容：{str(e)}"),
                title_padding=ft.padding.all(15),
            )
            app.page.open(dlg)
