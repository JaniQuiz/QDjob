import flet as ft
from globalApp import app, AppBarStatus
from QDjob import MainApp

mainApp = MainApp()

MAIN_ACTION = [
    ft.FilledButton(
        "执行全部配置",
        icon=ft.Icons.NOT_STARTED_OUTLINED,
        on_click=lambda e: mainApp.run(),
    ),
    ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ADD),
                        ft.Text("添加新配置"),
                    ]
                ),
                on_click=lambda _: app.mainView.addConfig(),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.EDIT),
                        ft.Text("批量编辑"),
                    ]
                ),
                on_click=lambda _: app.configPanel.setEditable(True),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.SETTINGS_SUGGEST),
                        ft.Text("更多设置"),
                    ]
                ),
                on_click=lambda _: app.view.switch("SettingsView"),
            ),
        ],
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(0),
        ),
    ),
]


def completeEditAction(e):
    app.configPanel.setEditable(False)


def deleteAndCompleteEditAction(e):
    app.configPanel.deleteSelected()
    app.configPanel.setEditable(False)


EDIT_ACTION = [
    ft.FilledButton(
        "删除",
        icon=ft.Icons.DELETE,
        on_click=deleteAndCompleteEditAction,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_400,  # 红色背景
            color=ft.Colors.WHITE,  # 白色文字
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
    ),
    ft.FilledButton(
        "完成",
        icon=ft.Icons.CHECK,
        on_click=completeEditAction,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_400,  # 绿色背景
            color=ft.Colors.WHITE,  # 白色文字
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
    ),
]

CONFIG_DETAIL_ACTION = [
    ft.FilledButton(
        "编辑配置",
        icon=ft.Icons.EDIT,
        on_click=lambda e: app.configDetailView.edit(),
    )
]

CONFIG_EDIT_ACTION = [
    ft.FilledButton(
        "保存",
        icon=ft.Icons.SAVE,
        on_click=lambda e: app.configEditView.save(),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.TEAL_ACCENT_700,
            color=ft.Colors.TEAL_900,
            shape=ft.RoundedRectangleBorder(radius=5),
        )
    )
]

SETTINGS_ACTION = [
    ft.FilledButton(
        "保存",
        icon=ft.Icons.SAVE,
        on_click=lambda e: app.settingsView.save(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=5),
        )
    )
]


class AppBar(ft.AppBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.leading = ft.Icon(ft.Icons.PALETTE)
        self.leading_width = 40
        self.title = ft.Text("QDJob")
        self.center_title = False
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST

        self.status = AppBarStatus.MAIN

        self.backButton = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(0),
            ),
            on_click=lambda e: self.back(e),
        )

        self.logoIcon = ft.Icon(ft.Icons.PALETTE)

        self.change_bar(self.status)

    def back(self, e):
        if self.status == AppBarStatus.CONFIG_DETAIL:
            app.view.switch("MainView")
        elif self.status == AppBarStatus.CONFIG_EDIT:
            app.view.switch("ConfigDetailView", user=app.configEditView.user)
        elif self.status == AppBarStatus.SETTINGS:
            app.view.switch("MainView")

    def show_back_button(self, enable: bool):
        if enable:
            self.leading = self.backButton
        else:
            self.leading = self.logoIcon

    def change_bar(self, status: AppBarStatus):
        self.status = status
        actions = None
        if status == AppBarStatus.MAIN:
            actions = MAIN_ACTION
            self.title = ft.Text("QDJob")
            self.show_back_button(False)
            self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        elif status == AppBarStatus.EDIT:
            actions = EDIT_ACTION
            self.title = ft.Text("QDJob")
            self.show_back_button(False)
            self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        elif status == AppBarStatus.CONFIG_DETAIL:
            actions = CONFIG_DETAIL_ACTION
            self.title = ft.Text("QDJob - 配置详情")
            self.show_back_button(True)
            self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        elif status == AppBarStatus.CONFIG_EDIT:
            actions = CONFIG_EDIT_ACTION
            self.title = ft.Text("QDJob - 编辑配置")
            self.show_back_button(True)
            self.bgcolor = ft.Colors.LIGHT_BLUE_400
        elif status == AppBarStatus.SETTINGS:
            actions = SETTINGS_ACTION
            self.title = ft.Text("QDJob - 设置")
            self.show_back_button(True)
            self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST

        self.actions = [
            ft.Container(
                content=ft.Row(actions, spacing=16),
                padding=ft.Padding(top=0, bottom=0, left=0, right=10),
            ),
        ]
