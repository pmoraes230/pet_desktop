import customtkinter as ctk
import app.core.colors as colors

class LoginForm(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")

        ctk.CTkLabel(
            self,
            text="Acesse sua conta",
            font=("Inter", 26, "bold"),
            text_color="#1F2937"
        ).pack(anchor="w", padx=60, pady=(60, 10))

        ctk.CTkLabel(
            self,
            text="Preencha seus dados para continuar.",
            font=("Inter", 13),
            text_color="#6B7280"
        ).pack(anchor="w", padx=60)

        self.email = ctk.CTkEntry(
            self,
            placeholder_text="seu@email.com",
            height=44,
            corner_radius=12
        )
        self.email.pack(fill="x", padx=60, pady=15)

        self.password = ctk.CTkEntry(
            self,
            placeholder_text="••••••••",
            show="•",
            height=44,
            corner_radius=12
        )
        self.password.pack(fill="x", padx=60)

        ctk.CTkButton(
            self,
            text="Entrar",
            height=46,
            corner_radius=12,
            fg_color=colors.BRAND_DARK_TEAL,
            hover_color=colors.BRAND_DARK_TEAL_HOVER
        ).pack(fill="x", padx=60, pady=25)
