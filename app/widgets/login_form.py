import customtkinter as ctk

class LoginForm(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(
            self,
            text="Acesse sua conta",
            font=("Arial", 26, "bold"),
            text_color="#1F2937"
        ).grid(row=0, padx=60, pady=(60, 10), sticky="w")

        email = ctk.CTkEntry(
            self,
            placeholder_text="seu@email.com",
            height=44,
            corner_radius=12
        )
        email.grid(row=1, padx=60, sticky="ew")

        senha = ctk.CTkEntry(
            self,
            placeholder_text="Senha",
            show="•",
            height=44,
            corner_radius=12
        )
        senha.grid(row=2, padx=60, pady=10, sticky="ew")

        ctk.CTkButton(
            self,
            text="Entrar",
            height=44,
            corner_radius=12,
            fg_color="#7A1FD1",
            hover_color="#6A1BC2"
        ).grid(row=3, padx=60, pady=20, sticky="ew")

        ctk.CTkLabel(
            self,
            text="Não tem conta? Criar cadastro",
            font=("Arial", 12),
            text_color="#6B7280"
        ).grid(row=4, padx=60, sticky="w")
