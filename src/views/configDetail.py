import flet as ft
from globalApp import app, AppBarStatus
from config import ConfigUsers, ConfigUserCookieKeys


class ConfigDetailView(ft.Column):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.scroll = ft.ScrollMode.HIDDEN
        self.user = None

    def on_cookie_tap(self, key, text):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    key.value,
                                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                                ),
                                ft.IconButton(
                                    ft.Icons.COPY,
                                    on_click=lambda _: app.page.set_clipboard(text),
                                    icon_size=12,
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.all(0),
                                    )
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Text(text, no_wrap=False),
                        ft.IconButton(
                            ft.Icons.CLOSE, on_click=lambda _: app.page.close(bs)
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
                padding=50,
            ),
            open=False,
        )

        app.page.open(bs)

    def load_config(self, user: ConfigUsers):
        tasks = []
        for key, value in user.config["tasks"].items():
            tasks.append(ft.Checkbox(label=key, value=value, disabled=True))

        cookies = []
        desc = {
            ConfigUserCookieKeys.APP_ID: "应用ID",
            ConfigUserCookieKeys.AREA_ID: "地区ID",
            ConfigUserCookieKeys.LANG: "语言",
            ConfigUserCookieKeys.MODE: "模式",
            ConfigUserCookieKeys.BAR: "条形码",
            ConfigUserCookieKeys.QIDTH: "宽度",
            ConfigUserCookieKeys.QID: "问题ID",
            ConfigUserCookieKeys.YWKEY: "业务关键字",
            ConfigUserCookieKeys.YWGUID: "业务全局唯一标识",
            ConfigUserCookieKeys.UUID: "用户唯一标识",
            ConfigUserCookieKeys.CMFU_TOKEN: "CMFU令牌",
            ConfigUserCookieKeys.QDINFO: "QD信息",
        }
        for key in ConfigUserCookieKeys:
            value = user.cookie[key]
            cookies.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(key.value)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    value if value else " - ",
                                    no_wrap=False,  # 允许换行
                                    max_lines=2,  # 最多显示3行
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                width=150,  # 正确：Container 可以设置宽度
                                expand=True,  # 横向拉满
                            ),
                            on_tap=lambda e, v=value, k=key: self.on_cookie_tap(k, v),
                        ),
                        ft.DataCell(ft.Text(desc.get(key, " - "))),
                    ],
                )
            )

        self.controls = [
            ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            user.username,
                            theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                            color=ft.Colors.PRIMARY,
                            badge=ft.Badge(
                                text=(
                                    "cookie 有效"
                                    if user.cookie.isValid()
                                    else "cookie 无效"
                                ),
                                bgcolor=(
                                    ft.Colors.LIGHT_GREEN_ACCENT_100
                                    if user.cookie.isValid()
                                    else ft.Colors.DEEP_ORANGE
                                ),
                                text_color=ft.Colors.BLACK87,
                                offset=ft.Offset(20, 10),
                            ),
                        ),
                        expand=True,  # 横向拉满
                        alignment=ft.alignment.center,  # 内容水平居中
                    ),
                    ft.Container(
                        content=ft.Text("任务"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        expand=True,  # 横向拉满
                        padding=10,  # 可选：让内容不贴边
                    ),
                    ft.GridView(
                        controls=tasks,
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
                                    " 当前为默认配置 ",
                                    bgcolor=ft.Colors.PRIMARY,
                                    color=ft.Colors.ON_PRIMARY,
                                ),
                            ]
                        ),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        expand=True,  # 横向拉满
                        padding=10,  # 可选：让内容不贴边
                    ),
                    ft.Text(
                        "Mozilla/5.0 (Linux; Android 15; V2171A Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/137.0.7151.115 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.417/1636/1000009/vivo/QDShowNativeLoading",
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("配置项")),
                            ft.DataColumn(ft.Text("值")),
                            ft.DataColumn(ft.Text("说明")),
                        ],
                        rows=cookies,
                        expand=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ]

        self.update()

    def on_switch(self, user):
        self.user = user
        self.load_config(user)
        app.appBar.change_bar(AppBarStatus.CONFIG_DETAIL)
    def edit(self):
        app.view.switch("ConfigEditView", user=self.user)
