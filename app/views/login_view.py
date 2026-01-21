import customtkinter as ctk
from app.widgets.left_panel import LeftPanel
from app.widgets.login_form import VetAuthForm

class LoginView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True, fill="both")

        # bg-gray-50
        self.configure(fg_color="#F5F6FA")

        # Card central (bg-white max-w-5xl h-[85vh])
        self.card = ctk.CTkFrame(
            self,
            width=1100,
            height=650,
            fg_color="white",
            corner_radius=24
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.grid_propagate(False)

        self.card.grid_columnconfigure((0, 1), weight=1)
        self.card.grid_rowconfigure(0, weight=1)

        LeftPanel(self.card).grid(row=0, column=0, sticky="nsew")
        VetAuthForm(self.card).grid(row=0, column=1, sticky="nsew")
