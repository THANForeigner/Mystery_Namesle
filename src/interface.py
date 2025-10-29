import flet as ft
import os
import sys
import asyncio
from src.logic import NamesleLogic
from src.board import InputBoxes
from src.popup import PopUpWindow
from src.loading_page import LoadingPage
from src.help import Help
PERCENT_COLOR = {
    0: "#FFFFFF",
    10: "#898989",
    21: "#90895B",
    41: "#C0B836",
    61: "#E6891E",    
    81: "#D84315",      
    100: "#00C853"      
}

def get_asset_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Namesle:
    async def initialize_game(self):
        self.loading_page = LoadingPage(self.page)
        self.page.overlay.append(self.loading_page)
        self.show_loading(True)
        self.page.update()
        self.logic = await asyncio.to_thread(NamesleLogic)
        self.show_loading(False)
        self.page.update()     
        self.input_boxes = InputBoxes()
        self.main_content_column = self.create_main_content()
        self.game_over_window = PopUpWindow(
            title="",
            message="",
            on_restart=self.restart_game_and_close_window,
            on_close=self.close_game_over_window
        )
        self.page.add(self.main_content_column)
        self.page.overlay.append(self.game_over_window)
        self.input_boxes.update_boxes_display(
            self.logic.guesses, 
            self.logic.current_guess, 
            self.logic.current_percentage, 
            self.logic.streak, 
            self.game_over, 
            self.logic.num_guesses, 
            self.logic.max_guesses
        )
        self.help_control = Help(self.page)
        self.page.overlay.append(self.help_control) 
        self.help_control.show_initial_popup()
        
    def __init__(self, page = ft.Page):
        self.page=page
        font_path = get_asset_path(os.path.join("data", "karnakcondensed-normal-700.ttf"))
        page.fonts = {"default" : font_path}
        self.page.title = "Wordle Mystery"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.bgcolor = "#3E1555"
        self.game_over = False
        self.restarting = False
        self.page.on_keyboard_event = self.on_keyboard_event
        self.page.run_task(self.initialize_game)
        
        
    def show_loading(self, is_loading: bool):
        self.loading_page.is_running=is_loading
        self.loading_page.run_loading()
        self.page.update()
    
    def set_loading_state(self, is_loading:bool):
        self.input_boxes.set_loading_state(is_loading, self.logic.num_guesses, self.page)
    
    def on_keyboard_event(self, e: ft.KeyboardEvent):
        if self.game_over:
            return
        key = e.key.upper()
        if key == "BACKSPACE":
            self.handle_keypress_remove()
        elif key == "ENTER":
            if len(self.logic.current_guess) > 0:
                self.page.run_task(self.handle_keypress_submit)
        elif key.isalpha() or key.isnumeric() or key == "SPACE":
            char = " " if key == "SPACE" else key
            self.handle_keypress_add(char)
        self.page.update()

    def handle_keypress_add(self, char: str):
        if self.logic.add_letter(char):
            self.input_boxes.update_boxes_display(
                self.logic.guesses, 
                self.logic.current_guess, 
                self.logic.current_percentage, 
                self.logic.streak, 
                self.game_over, 
                self.logic.num_guesses, 
                self.logic.max_guesses
            )
            
    def handle_keypress_remove(self):
        self.logic.remove_letter()
        self.input_boxes.update_boxes_display(
                self.logic.guesses, 
                self.logic.current_guess, 
                self.logic.current_percentage, 
                self.logic.streak, 
                self.game_over, 
                self.logic.num_guesses, 
                self.logic.max_guesses
        )

    async def handle_keypress_submit(self):
        if len(self.logic.current_guess) == 0:
            return
        self.set_loading_state(True)
        try:
            result = await asyncio.to_thread(self.logic.submit_word)
        except Exception as e:
            result = None
        self.set_loading_state(False)
        if result is None:
            return
        hint_word, win = result
        self.input_boxes.update_boxes_display(
                self.logic.guesses, 
                self.logic.current_guess, 
                self.logic.current_percentage, 
                self.logic.streak, 
                self.game_over, 
                self.logic.num_guesses, 
                self.logic.max_guesses
        )
        if win:
            self.game_over = True
            self.input_boxes.update_percent_bar(100, self.logic.streak)
            self.game_over = True
            if self.logic.max_streak==len(self.input_boxes.guess_boxes):
                self.show_game_over_dialog("You Win!", f"Perfect play!", ft.Colors.GREEN_400)
            else:
                self.show_game_over_dialog("You Win!", f"Max streak: {self.logic.max_streak}", ft.Colors.GREEN_400)
        elif self.logic.num_guesses >= self.logic.max_guesses:
            self.game_over = True
            self.show_game_over_dialog("Game Over", f"You ran out of guesses! The word was **{self.logic.hidden_word}**.", ft.Colors.YELLOW_400)  
        else:
            self.input_boxes.update_boxes_display(
                self.logic.guesses, 
                self.logic.current_guess, 
                self.logic.current_percentage, 
                self.logic.streak, 
                self.game_over, 
                self.logic.num_guesses, 
                self.logic.max_guesses
            )
        
    def create_main_content(self) -> ft.Column:
        input_boxes_column_content = self.input_boxes.create_input_boxes(self.logic.max_guesses, self.logic.max_length)
        input_boxes_column_with_label = ft.Column(
            controls=[
                ft.Text("GUESSES", size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                input_boxes_column_content,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10, 
        )
        percent_bar_column_with_label = self.input_boxes.create_percent_bar()
        game_area_row = ft.Row(
            controls=[
                input_boxes_column_with_label,
                ft.Container(width=70), 
                percent_bar_column_with_label,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
        )
        framed_game_area = ft.Container(
            content=game_area_row,
            padding=30, 
            bgcolor="#492288",
            border_radius=20, 
            border=ft.border.all(5, "#B274FF"), 
            shadow=ft.BoxShadow(
                spread_radius=2, blur_radius=20,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK), offset=ft.Offset(0, 10),
            )
        )
        
        return ft.Column(
            alignment = ft.MainAxisAlignment.START,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER, 
            controls = [
                ft.Container(height=20), # Space from top
                ft.Text("Mystery Namesle", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                framed_game_area,
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        ) 
    
    def draw_ui(self):
        self.page.update()
    
    def show_game_over_dialog(self, title: str, message: str, color: ft.Colors):
        self.game_over_window.update_content(title, message, color)
        self.game_over_window.visible = True
        self.restarting = True
        self.page.update()
        async def auto_fade():
            await asyncio.sleep(3)
            if self.restarting:
                self.restart_game_and_close_window()
                self.restarting = False
                self.page.update()
        self.page.run_task(auto_fade)
    
    async def restart(self):
        self.page.clean()
        self.input_boxes = InputBoxes()
        self.game_over = False
        self.restarting = False
        self.main_content_column = self.create_main_content()
        self.page.add(self.main_content_column)
        self.show_loading(True)
        self.page.update()
        self.logic = await asyncio.to_thread(NamesleLogic)
        self.show_loading(False) 
        self.page.update()
        self.input_boxes.update_boxes_display(
            self.logic.guesses, 
            self.logic.current_guess, 
            self.logic.current_percentage, 
            self.logic.streak, 
            self.game_over, 
            self.logic.num_guesses, 
            self.logic.max_guesses
        )
    
    def close_game_over_window(self, e = None):
        self.game_over_window.visible = False
        self.restarting = False
        self.page.update()
    
    def restart_game_and_close_window(self, e = None):
        self.close_game_over_window(e) 
        self.page.run_task(self.restart)
        self.page.update()