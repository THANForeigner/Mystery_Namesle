import flet as ft
import asyncio
class LoadingPage (ft.Container):
    def __init__(self, page = ft.Page):
        super().__init__(
            alignment=ft.alignment.center,
            expand = True,
            bgcolor=ft.Colors.with_opacity(0.8, "#3E1555"),
            visible = False
        ),
        self.page = page
        self.visible=False
        self.is_running = False
        self.title_up = ft.Text(
            "Mystery Namesle",
            size=40,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            font_family="default"
        )
        self.title_down = ft.Container(
            content = ft.Text(
                "Mystery Namesle",
                size = 40,
                color = ft.Colors.PURPLE_ACCENT_700,
                weight = ft.FontWeight.BOLD,
                font_family = "default"
            ),
        )
        
        self.animated_title = ft.AnimatedSwitcher(
            self.title_up,
            transition = ft.AnimatedSwitcherTransition.SCALE,
            duration = 500,
            reverse_duration = 500,
            switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
            switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
        )
        
        self.content = ft.Column(
            controls = [
                ft.Container(
                    content = self.animated_title,
                    height = 60,
                    alignment = ft.alignment.center,
                ),
                ft.Container(height=30),
                ft.Container(
                    width = 200,
                    content = ft.ProgressBar(
                        color = ft.Colors.PURPLE_ACCENT_100,
                        bgcolor = ft.Colors.WHITE30,
                        bar_height=10,
                    )
                ),
                ft.Text(
                    "LOADING...",
                    size = 20,
                    color = ft.Colors.WHITE,
                    weight = ft.FontWeight.BOLD,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
    def start_bounce_animation(self):
        """Task to continuously bounce the title."""
        async def bounce_switcher():
            while self.visible:
                # Set to down state
                self.animated_title.content = self.title_down
                self.page.update()
                await asyncio.sleep(0.7)
                
                # Set to up state
                self.animated_title.content = self.title_up
                self.page.update()
                await asyncio.sleep(0.7)
        
        if self.visible:
            self.page.run_task(bounce_switcher)

    # Override the setter for 'visible' to control the animation
    def run_loading(self):
        if self.is_running:
            self.visible=True
            self.start_bounce_animation()
        else:
            self.visible=False
        if self.page:
            self.page.update()