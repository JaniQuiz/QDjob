import os
import flet as ft

from globalApp import app
from components import AppBar, ConfigPanel
from views import MainView, ConfigDetailView, ConfigEditView, SettingsView
from view import ViewManager
from config import config

FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")

# 校验外部依赖库是否工作
from test import test_requests, test_pycryptodome

test_requests()
test_pycryptodome()


def main(_page: ft.Page):
    app.page = _page
    app.appBar = AppBar()
    app.mainView = MainView()
    app.view = ViewManager(_page)

    page = _page

    page.title = "AppBar Example"

    page.appbar = app.appBar

    app.configDetailView = ConfigDetailView()
    app.configEditView = ConfigEditView()
    app.settingsView = SettingsView()

    app.view.add_page(app.mainView, "MainView")
    app.view.add_page(app.configDetailView, "ConfigDetailView")
    app.view.add_page(app.configEditView, "ConfigEditView")
    app.view.add_page(app.settingsView, "SettingsView")

    app.page.add(app.view)


ft.app(main)
