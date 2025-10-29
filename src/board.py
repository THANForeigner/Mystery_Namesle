import flet as ft
from time import sleep
PERCENT_COLOR = {
    0: "#FFFFFF",
    10: "#898989",
    21: "#90895B",
    41: "#C0B836",
    61: "#E6891E",    
    81: "#D84315",      
    100: "#00C853"      
}

class InputBoxes:
    def __init__(self):
        self.percent_bar_fill = None 
        self.percent_text = None 
        self.streak_text = 0 
        self.guess_boxes: list[ft.Container] = []
        
    def get_color(self, percent: int) -> str:
        return next(PERCENT_COLOR[p] for p in sorted(PERCENT_COLOR, reverse=True) if percent >= p)
        
    def create_input_boxes(self, max_guesses: int, max_length: int) -> ft.Column:
        for i in range(max_guesses):
            text_field=ft.TextField(
                value="", 
                text_align = ft.TextAlign.CENTER,
                read_only = (i != 0), 
                border=ft.InputBorder.NONE, 
                bgcolor=ft.Colors.TRANSPARENT,
                content_padding=0,
                text_size=28, 
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), 
                max_length=max_length, 
                cursor_height=0, 
                cursor_color=ft.Colors.TRANSPARENT,
                autofocus=True if i == 0 else False,
                ignore_pointers=True
            )
            loading_overlay = ft.Container(
                content=ft.ProgressBar(
                    value=None, 
                    height=5,
                    color=ft.Colors.LIGHT_BLUE_ACCENT_100,
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
                visible=False,
                alignment=ft.alignment.bottom_center,
                height=65, 
                width=500,  
                padding=ft.padding.only(bottom=5), 
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            )
            box_content_stack = ft.Stack(
                controls=[
                    text_field, 
                    loading_overlay,
                ]
            )
            box = ft.Container(
                content = box_content_stack,
                width = 500, 
                height = 65,
                bgcolor = ft.Colors.WHITE10, 
                border = ft.border.all(3, ft.Colors.GREY_700), 
                border_radius = 10, 
                scale=ft.Scale(scale=1),
                animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
                shadow=None,
            )
            self.guess_boxes.append(box)
        
        return ft.Column(
            controls=self.guess_boxes,
            spacing=8, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def update_boxes_display(self, history: list[tuple[str,int]], current_guess: str, percent: int, streak: int, game_over: bool, current_box: int, max_guesses: int):
        self.current_guess_box = current_box 
        for i in range(max_guesses):
            log = history[i] if i < len(history) else None
            self.guess_boxes[i].scale.scale = 1.0
            box_stack = self.guess_boxes[i].content
            text_field_control = box_stack.controls[0] 
            loading_overlay = box_stack.controls[1]
            loading_overlay.visible = False
            text_field_control.read_only = game_over or (i != current_box) 
            if i == current_box and not game_over:
                text_field_control.value = current_guess
                self.guess_boxes[i].border = ft.border.all(3, ft.Colors.LIGHT_BLUE_ACCENT_200)
                self.guess_boxes[i].shadow = ft.BoxShadow(
                    spread_radius=1, blur_radius=10, 
                    color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_ACCENT_400), offset=ft.Offset(0, 5),
                )
                self.guess_boxes[i].bgcolor = ft.Colors.WHITE10 
            elif log:
                text, percent = log
                text_field_control.value = text
                self.guess_boxes[i].bgcolor = self.get_color(percent) 
                self.guess_boxes[i].border = ft.border.all(3, self.get_color(percent)) 
                self.guess_boxes[i].shadow = None 
            else:
                text_field_control.value = ""
                self.guess_boxes[i].border = ft.border.all(3, ft.Colors.GREY_700)
                self.guess_boxes[i].bgcolor = ft.Colors.WHITE10 
                self.guess_boxes[i].shadow = None

            text_field_control.update()
            self.guess_boxes[i].update() 
        
        self.update_percent_bar(percent, streak)

    def create_percent_bar(self) -> ft.Column:
        self.percent_text = ft.Text("0%", font_family = "default", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.percent_bar_fill = ft.Container(
            width = 40,
            height = 0, 
            bgcolor = self.get_color(0), 
            alignment=ft.alignment.bottom_center,
            animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT)
        )
        percent_bar_track = ft.Container(
            width = 40,
            height = 340, 
            content = ft.Column([self.percent_bar_fill], spacing=0, alignment=ft.MainAxisAlignment.END), 
            bgcolor = ft.Colors.BLACK54,
            border_radius= 5,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
        )
        self.streak_text = ft.Text("0", font_family = "default", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        return ft.Column(
            controls=[
                ft.Text("Streak", font_family = "default", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), 
                self.streak_text,
                ft.Container(height=10),
                percent_bar_track,
                ft.Container(height=5),
                self.percent_text, 
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
    def update_percent_bar(self, percent: int, streak: int):
        max_bar_height = 340
        new_height = (percent / 100) * max_bar_height
        new_color = self.get_color(percent)
        self.percent_bar_fill.height = new_height
        self.percent_bar_fill.bgcolor = new_color
        self.streak_text.value = str(streak)
        self.percent_text.value = f"{percent}%"    
        self.percent_bar_fill.update()
        self.streak_text.update()
        self.percent_text.update()
        
    def set_loading_state(self, is_loading: bool, current_box_id: int, page: ft.Page):
        if current_box_id >= len(self.guess_boxes): return
        current_box = self.guess_boxes[current_box_id]
        if isinstance(current_box.content, ft.Stack) and len(current_box.content.controls) > 1:
            text_field = current_box.content.controls[0]
            loading_overlay = current_box.content.controls[1]  
            loading_overlay.visible = is_loading
            text_field.read_only = is_loading
            if is_loading:
                current_box.border = ft.border.all(3, ft.Colors.YELLOW_ACCENT_400)
            else:
                pass
            loading_overlay.update()
            current_box.update()
            page.update()