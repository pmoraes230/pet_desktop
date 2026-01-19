import customtkinter as ctk

class LeftPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master,
            fg_color="#7A1FD1",
            corner_radius=24
        )

        self.grid_rowconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            self,
            text="Corações em Patas",
            font=("Arial", 20, "bold"),
            text_color="white"
        ).grid(row=0, padx=40, pady=40, sticky="nw")

        ctk.CTkLabel(
            self,
            text="Bem-vindo de\nvolta!",
            font=("Arial", 36, "bold"),
            text_color="white",
            justify="left"
        ).grid(row=1, padx=40, sticky="w")

        ctk.CTkLabel(
            self,
            text="Acompanhe a saúde emocional\n"
                 "e física do seu pet em um só lugar.",
            font=("Arial", 16),
            text_color="#E5D9FF",
            justify="left"
        ).grid(row=2, padx=40, pady=40, sticky="sw")
