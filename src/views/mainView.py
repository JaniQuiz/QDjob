import flet as ft
from globalApp import app, AppBarStatus
from components import AppBar, ConfigPanel, AboutCard
from utils import load_config
from config import config
from pprint import pprint


class MainView(ft.Column):
    def __init__(self):
        super().__init__()

        app.configPanel = ConfigPanel()
        

        self.controls = [
            app.configPanel,
            AboutCard(),
        ]
        self.expand = True  # 垂直拉满

        # self.alignment=ft.MainAxisAlignment.CENTER  # 垂直居中
        # self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH  # 横向拉伸

    def on_switch(self):
        app.configPanel.updateData()
        app.appBar.change_bar(AppBarStatus.MAIN)

    def addConfig(self):
        print("添加新配置")
        usernameEdit = ft.TextField(
            label="用户名（配置名称）", hint_text="请输入新配置的用户名（配置名称）"
        )

        def confirm_add(e):
            username = usernameEdit.value.strip()
            user = config.addUser(username)
            app.view.switch("ConfigEditView", user=user)
            app.page.close(dlg_modal)

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("输入用户名（配置名称）"),
            content=usernameEdit,
            actions=[
                ft.TextButton("确认", on_click=lambda e: confirm_add(e)),
                ft.TextButton("取消", on_click=lambda e: app.page.close(dlg_modal)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        app.page.open(dlg_modal)
