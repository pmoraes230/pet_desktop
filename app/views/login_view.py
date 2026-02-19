import customtkinter as ctk
from app.views.left_panel import LeftPanel
from app.views.login_form import VetAuthForm

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.pack(expand=True, fill="both")
        self.configure(fg_color="#F5F6FA")

        self.card = ctk.CTkFrame(self, width=1100, height=650, fg_color="white", corner_radius=24)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.grid_propagate(False)
        self.card.grid_columnconfigure((0, 1), weight=1)
        self.card.grid_rowconfigure(0, weight=1)

        LeftPanel(self.card).grid(row=0, column=0, sticky="nsew")
        
        # O self.card aqui será o master do VetAuthForm
        self.form = VetAuthForm(self.card, on_login_success=on_login_success)
        self.form.grid(row=0, column=1, sticky="nsew")