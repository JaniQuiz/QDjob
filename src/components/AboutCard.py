import flet as ft

class AboutCard(ft.Card):
    def __init__(self):
        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("项目名：QDjob", size=12, weight=ft.FontWeight.BOLD),
                        ft.Text("作者：JaniQuiz", size=12),
                        ft.TextButton(
                            text="GitHub: https://github.com/JaniQuiz/QDjob",
                            url="https://github.com/JaniQuiz/QDjob",
                        ),
                        ft.Text(
                            "开源声明：该项目为开源免费项目，不会收取任何费用",
                            size=12,
                        ),
                    ],
                    spacing=2,
                ),
                padding=10,
                alignment=ft.alignment.center,
                expand=False,
            )
        )
