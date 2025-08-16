import flet as ft
from globalApp import app, AppBarStatus
from config import (
    config,
    ConfigKeys,
    ConfigUsers,
    ConfigUsersKeys,
    ConfigUserCookieKeys,
)


class ConfigEditView(ft.Column):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.scroll = ft.ScrollMode.HIDDEN
        self.user = None

    def load_config(self, user: ConfigUsers):
        self.tasks_checkbox = {}
        for key, value in user.config["tasks"].items():
            self.tasks_checkbox[key] = ft.Checkbox(
                label=key, value=value, disabled=False
            )

        self.usernameEdit = ft.TextField(
            label="用户名",
            hint_text="请输入用户名（不要和已有重复）",
            value=user.username,
        )

        self.userAgentEdit = ft.TextField(
            label="User Agent 留空则默认采用全局默认值",
            multiline=True,
            min_lines=3,
            max_lines=10,
            hint_text=f"全局默认：{config[ConfigKeys.DEFAULT_USER_AGENT]}",
            value=user[ConfigUsersKeys.USER_AGENT],
        )

        print("输出内容", user.cookie.cookies)

        cookie_str = "; ".join(f"{key}={value}" for key, value in user.cookie.cookies.items())

        self.cookieEdit = ft.TextField(
            label="Cookie 原始字符串",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text=f"输入示例：appid=xxx;areaid=xxx;lang=xxx; ...",
            value=cookie_str,
        )

        self.controls = [
            ft.Column(
                [
                    ft.Container(
                        content=self.usernameEdit,
                        expand=True,  # 横向拉满
                        alignment=ft.alignment.center,  # 内容水平居中
                        padding=5,  # 可选：让内容不贴边
                    ),
                    ft.Container(
                        content=ft.Text("任务"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        expand=True,  # 横向拉满
                        padding=10,  # 可选：让内容不贴边
                    ),
                    ft.GridView(
                        controls=list(self.tasks_checkbox.values()),
                        max_extent=180,  # 每列最大宽度
                        child_aspect_ratio=3,  # 宽高比
                        spacing=10,
                        run_spacing=10,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("User Agent"),
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
                    self.userAgentEdit,
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Cookie配置"),
                                ft.Text(
                                    " 填写原始字符串开始末尾不要有空格和空行 ",
                                    size=12,
                                ),
                            ]
                        ),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        expand=True,  # 横向拉满
                        padding=10,  # 可选：让内容不贴边
                    ),
                    self.cookieEdit,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ]

        self.update()

    def on_switch(self, user):
        self.user = user
        self.load_config(user)
        app.appBar.change_bar(AppBarStatus.CONFIG_EDIT)

    def save(self):
        print("保存配置")
        try:
            self.user[ConfigUsersKeys.USERNAME] = self.usernameEdit.value
            self.user[ConfigUsersKeys.USER_AGENT] = self.userAgentEdit.value
            self.user[ConfigUsersKeys.SIGN_IN_TASK] = self.tasks_checkbox.get(
                ConfigUsersKeys.SIGN_IN_TASK.value
            ).value
            self.user[ConfigUsersKeys.INCENTIVE_FRAGMENT_TASK] = (
                self.tasks_checkbox.get(
                    ConfigUsersKeys.INCENTIVE_FRAGMENT_TASK.value
                ).value
            )
            self.user[ConfigUsersKeys.EXTRA_INCENTIVE_TASK] = self.tasks_checkbox.get(
                ConfigUsersKeys.EXTRA_INCENTIVE_TASK.value
            ).value
            self.user[ConfigUsersKeys.CHAPTER_CARD_TASK] = self.tasks_checkbox.get(
                ConfigUsersKeys.CHAPTER_CARD_TASK.value
            ).value
            self.user[ConfigUsersKeys.DAILY_LOTTERY_TASK] = self.tasks_checkbox.get(
                ConfigUsersKeys.DAILY_LOTTERY_TASK.value
            ).value
            self.user.cookie.updateFromStr(self.cookieEdit.value)
            
            app.view.switch("ConfigDetailView", user=self.user)
        except Exception as e:
            dlg = ft.AlertDialog(
                title=ft.Text("配置项出错"),
                content=ft.Text(f"报错内容：{str(e)}"),
                title_padding=ft.padding.all(15),
            )
            app.page.open(dlg)
