import customtkinter as ctk
from app.widgets.left_panel import LeftPanel
from app.widgets.login_form import LoginForm

class LoginView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True, fill="both")

        self.configure(fg_color="#F5F6FA")

        # Container central (card)
        self.card = ctk.CTkFrame(
            self,
            width=1100,
            height=650,
            corner_radius=24,
            fg_color="white"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.card.grid_propagate(False)
        self.card.grid_columnconfigure((0, 1), weight=1)
        self.card.grid_rowconfigure(0, weight=1)

        # Painel esquerdo
        LeftPanel(self.card).grid(row=0, column=0, sticky="nsew")

        # Painel direito
        LoginForm(self.card).grid(row=0, column=1, sticky="nsew")
