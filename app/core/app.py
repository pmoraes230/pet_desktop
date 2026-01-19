import customtkinter as ctk
import os
from app.views.login_view import LoginView
from app.core.theme import apply_theme

class PetApp:

    def __init__(self):
        apply_theme()

        self.app = ctk.CTk()
        self.app.title("PetMental")

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ICON_PATH = os.path.join(BASE_DIR, "assets", "pet.ico")

        if os.path.exists(ICON_PATH):
            self.app.iconbitmap(ICON_PATH)

        self.app.minsize(900, 600)
        self.app.after(0, lambda: self.app.state("zoomed"))

        self.show_login()

    def show_login(self):
        self.clear()
        LoginView(self.app)

    def clear(self):
        for widget in self.app.winfo_children():
            widget.destroy()

    def run(self):
        self.app.mainloop()
