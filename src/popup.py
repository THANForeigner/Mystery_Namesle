import flet as ft
class PopUpWindow (ft.Container):
    def __init__ (self, title: str, message: str, on_restart, on_close):
        self.dialog_color = ft.Colors.BLACK 
        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family="default"),
                        ft.Text(message, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family="default"),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("Play Again", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family="default"), 
                                    on_click=on_restart
                                ),
                                ft.TextButton(
                                    content=ft.Text("Close", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family="default"), 
                                    on_click=on_close
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                width=350,
                height=200, 
                padding=20,
                border_radius=10,
                bgcolor=self.dialog_color, 
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.5, self.dialog_color), 
                    offset=ft.Offset(0, 0),
                    blur_style=ft.ShadowBlurStyle.OUTER,
                ),
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK), 
            expand=True,
            visible=False,
        )
        self.title_control = self.content.content.controls[0]
        self.message_control = self.content.content.controls[1]
        self.dialog_content_container = self.content

    def update_content(self, title: str, message: str, color: ft.Colors):
        self.title_control.value = title
        self.message_control.value = message
        self.dialog_color = color 
        
        self.dialog_content_container.bgcolor = color
        self.dialog_content_container.shadow.color = ft.Colors.with_opacity(0.5, color)
        self.bgcolor = ft.Colors.with_opacity(0.8, color)
        
        self.message_control.value = message
        self.message_control.selectable = True
        
        self.update()

class PopUpWarning (ft.Container):
    def __init__ (self, title: str, message: str, on_close):
        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="default"),
                        ft.Text(message, size=24, color=ft.Colors.WHITE, font_family="default"),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("Close", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="default"), 
                                    on_click=on_close
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                width=350,
                height=200, 
                padding=20,
                border_radius=10,
                bgcolor=ft.Colors.RED_400,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.RED_400), 
                    offset=ft.Offset(0, 0),
                    blur_style=ft.ShadowBlurStyle.OUTER,
                ),
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.RED_400),
            expand=True,
            visible=False,
        )
        self.title_control = self.content.content.controls[0]
        self.message_control = self.content.content.controls[1]
    
    def update_content(self,message: str):
        self.message_control.value = message
        self.update()
  