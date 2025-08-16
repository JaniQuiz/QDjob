import flet as ft
from globalApp import app, AppBarStatus
from config import config, ConfigUsers, ConfigKeys, ConfigUsersKeys


class ConfigPanelItem(ft.ListTile):
    editable = False

    def __init__(self, user: ConfigUsers, parent=None):
        super().__init__()

        self.parent = parent
        self.user = user

        tasks = []

        for key, value in self.user.config["tasks"].items():
            if value:
                tasks.append(
                    ft.Text(
                        key,
                        size=12,
                        italic=True,
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                    )
                )

        self.title = ft.Container(
            content=ft.Text(
                user.username,
                theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                color=ft.Colors.PRIMARY,
                badge=ft.Badge(
                    text=("cookie 有效" if user.cookie.isValid() else "cookie 无效"),
                    bgcolor=(
                        ft.Colors.LIGHT_GREEN_ACCENT_100
                        if user.cookie.isValid()
                        else ft.Colors.DEEP_ORANGE
                    ),
                    text_color=ft.Colors.BLACK87,
                    offset=ft.Offset(20, 10),
                ),
            ),
        )

        self.subtitle = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=tasks if tasks else [ft.Text("No tasks available")],
                        scroll=ft.ScrollMode.AUTO,  # c超出自动滚动
                    ),
                    on_click=lambda e: None,  # 阻止冒泡
                ),
                ft.Text(
                    (
                        self.user[ConfigUsersKeys.USER_AGENT]
                        if self.user[ConfigUsersKeys.USER_AGENT]
                        else config[ConfigKeys.DEFAULT_USER_AGENT]
                    ),
                    size=10,
                    italic=True,
                ),
            ]
        )

        self._trailing = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text="编辑",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: app.view.switch(
                        "ConfigEditView", user=self.user
                    ),
                ),
                ft.PopupMenuItem(
                    text="删除",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: self.parent.remove(self),
                ),
            ]
        )

        self.trailing = self._trailing

        self.checkbox = ft.Checkbox(label="", value=False)

        self.on_click = self._on_click
        self.on_long_press = self._on_long_press

    def _on_click(self, e):
        if self.editable:
            print(f"Item is editable, toggling checkbox.")
            self.checkbox.value = not self.checkbox.value
            self.checkbox.update()
            return

        app.view.switch("ConfigDetailView", user=self.user)

    def _on_long_press(self, e):
        print(f"Long pressed on {self.title}")
        self.parent.setEditable(True)

    def setEditable(self, editable: bool):
        self.editable = editable

        print(f"Setting item editable to {editable}")

        if editable:
            self.checkbox.value = False
            self.leading = self.checkbox
            self.trailing = None
        else:
            self.leading = None
            self.trailing = self._trailing


class ConfigPanel(ft.Column):
    editable = False

    def __init__(self):
        super().__init__()

        self.updateData()
        self.scroll = ft.ScrollMode.HIDDEN
        self.expand = True  # 垂直拉满

    def setEditable(self, editable: bool):
        self.editable = editable

        for control in self.controls:
            if isinstance(control, ConfigPanelItem):
                control.setEditable(editable)

        app.appBar.change_bar(AppBarStatus.EDIT if editable else AppBarStatus.MAIN)

        app.page.update()  # Update the page to reflect changes

    def updateData(self):
        """刷新列表数据"""
        self.controls = []
        controls = []

        for username in config.listUsername():
            user = config.getUser(username)
            if user:
                controls.append(ConfigPanelItem(user, parent=self))

        if controls == []:
            controls.append(
                ft.Container(
                    content=ft.FilledButton(
                        "添加新配置",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: app.mainView.addConfig(),
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=ft.Padding(top=15, left=0, right=0, bottom=0),
                )
            )

        self.controls = controls

    def deleteSelected(self):
        selected_items = [
            control for control in self.controls if control.checkbox.value
        ]
        for item in selected_items:
            config.removeUser(item.user.username)
        self.updateData()
        self.update()

    def remove(self, item: ConfigPanelItem):
        if item in self.controls:
            config.removeUser(item.user.username)
            self.updateData()  # Refresh the list to ensure it's up-to-date
        self.update()
