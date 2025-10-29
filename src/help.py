import flet as ft
class Help(ft.Container):
    def __init__(self, page: ft.Page):
            super().__init__(
                visible=False, 
                alignment=ft.alignment.top_right,
            )
            self.page = page
            self.help_dialog = self.create_help_dialog()
            
            self.help_button = ft.IconButton(
                icon=ft.Icons.HELP_OUTLINE,
                icon_color="#FFFFFF",
                tooltip="Show Help/Rules",
                on_click=self.open_help,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    bgcolor=ft.Colors.with_opacity(0.1, "#B274FF")
                ),
            )
            self.content = ft.Container(
                content=self.help_button,
                padding=ft.padding.only(top=10, right=10),
                alignment=ft.alignment.top_right,
                width=page.width,
                height=page.height,
            )
            
            self.page.overlay.append(self.help_dialog)
            self.page.update()
            
    def create_help_dialog(self)->ft.AlertDialog:
        help_text = (
            "NAMESLE HELPS & RULES\n\n"  
            "The game will generate a one word hidden name (can be movies' name, companies' name, "
            "celebrities' name, common names, etc). Your job is to guess that name in 6 guesses."
            " In the guess box you can enter anything but one word only."
            "Each time you submit your guess the game will return a maximum three words hint and the "
            "bar on the right will change depend on how related your input to the hidden name.\n\n"
            "Good luck, cause you might need it!!!"
        )
        
        help = ft.AlertDialog(
            modal=True,
            title=ft.Text("Welcome to Namesle!", font_family = "default", weight=ft.FontWeight.BOLD),
            bgcolor="#B274FF",
            barrier_color=ft.Colors.with_opacity(0.5,"#6219BC"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        help_text,
                        size = 24,
                        selectable=True,
                        font_family = "default",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Divider(),
                    ft.Text("Happy guessing!", size=24, font_family = "default", weight=ft.FontWeight.BOLD),
                ],
                tight=True,
                ),
                padding=ft.padding.all(10)
            ),
            actions=[
                ft.TextButton(
                    content = ft.Text("GOT IT!", size=24, font_family = "default", weight=ft.FontWeight.BOLD, color = "#4A00C2"), 
                    on_click=self.close_help),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return help
    
    def open_help(self,e):
        self.page.dialog = self.help_dialog
        self.help_dialog.open = True
        self.page.update()
        
    def close_help(self,e):
        self.help_dialog.open = False
        self.visible = True
        self.page.update()
        
    def show_initial_popup(self):
        self.open_help(None)