import flet as ft

class ViewManager(ft.Stack):
    def __init__(self, page):
        super().__init__()

        self.page = page
        self.expand = True
        self._controls = {}
        self.current_idx = None  # 当前显示的页面key

    def add_page(self, view, idx):
        self._controls[idx] = view
        # 默认只让第一个页面可见，其余不可见
        if len(self._controls) == 1:
            view.visible = True
            self.current_idx = idx
        else:
            view.visible = False
        self.controls = list(self._controls.values())
        self.page.update()

    def remove_page(self, idx):
        if idx not in self._controls:
            raise NameError(f"Page with key {idx} does not exist.")
        if idx == self.current_idx:
            # 获取当前页面的索引
            index = self._controls.index(self._controls[idx])
            if index - 1 >= 0:
                self.current_idx = list(self._controls.keys())[
                    index - 1
                ]  # 切换到上一个页面
            elif index + 1 < len(self.controls):
                self.current_idx = list(self._controls.keys())[
                    index + 1
                ]  # 切换到下一个页面
            else:
                self.current_idx = None  # 如果没有其他页面，则设置为None

            if idx:
                self.switch(self.current_idx)

        del self._controls[idx]
        self.controls = list(self._controls.values())
        self.page.update()

    def switch(self, idx, **kwargs):
        if idx not in list(self._controls.keys()):
            raise NameError(f"Page with key {idx} does not exist.")

        for i, control in self._controls.items():
            # 如果被切换的页面有"on_switch"方法需要调用
            if i == idx:
                if hasattr(control, "on_switch"):
                    control.on_switch(**kwargs)
            control.visible = i == idx
        self.current_idx = idx
        self.page.update()
