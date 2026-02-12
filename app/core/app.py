import customtkinter as ctk
import os
from app.views.login_view import LoginView
from app.core.theme import apply_theme

class PetApp:

    def __init__(self):
        apply_theme()

        self.app = ctk.CTk()
        self.show_login()

    def show_login(self):
        self.clear()
        LoginView(self.app)

    def clear(self):
        for widget in self.app.winfo_children():
            widget.destroy()

    def run(self):
        self.app.mainloop()
