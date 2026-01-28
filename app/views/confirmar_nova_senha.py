import customtkinter as ctk

# Configuration
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class ChangePasswordApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Coração em patas - Trocar Senha")
        self.geometry("900x600")
        self.configure(fg_color="#F5F5F7")  # Light gray background

        # Main Container (The White Card)
        self.card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=30,
            width=600,
            height=500
        )
        self.card.pack(expand=True)
        self.card.pack_propagate(False) # Enforce size

        # --- Header / Logo Section ---
        self.header_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.header_frame.pack(anchor="nw", padx=40, pady=40)

        # Icon (Simulated with a rounded button)
        self.logo_icon = ctk.CTkButton(
            self.header_frame,
            text="🐾",  # Using an emoji to represent the paw prints
            font=("Arial", 20),
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#7D2AE8",  # Purple Brand Color
            hover=False  # Make it static
        )
        self.logo_icon.pack(side="left")

        # Brand Name
        self.brand_label = ctk.CTkLabel(
            self.header_frame,
            text="Coração em patas",
            font=("Arial", 16, "bold"),
            text_color="#000000"
        )
        self.brand_label.pack(side="left", padx=15)

        # --- Form Content Section ---
        self.content_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=100, pady=(0, 60))

        # Title
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Troque sua senha",
            font=("Arial", 28, "bold"),
            text_color="#000000"
        )
        self.title_label.pack(pady=(10, 5), anchor="w") # Align slightly left or center effectively via container
        self.title_label.pack_configure(anchor="center")

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="Preencha seus dados para continuar",
            font=("Arial", 13),
            text_color="#A0A0A0"
        )
        self.subtitle_label.pack(pady=(0, 30), anchor="center")

        # Field 1: Nova Senha
        self.lbl_pass = ctk.CTkLabel(
            self.content_frame,
            text="Nova senha",
            font=("Arial", 14, "bold"),
            text_color="#000000"
        )
        self.lbl_pass.pack(anchor="w", pady=(0, 5))

        self.entry_pass = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Informe a sua nova senha",
            height=45,
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA",
            text_color="#000000"
        )
        self.entry_pass.pack(fill="x", pady=(0, 20))

        # Field 2: Confirmar Senha
        self.lbl_confirm = ctk.CTkLabel(
            self.content_frame,
            text="Confirmar nova senha",
            font=("Arial", 14, "bold"),
            text_color="#000000"
        )
        self.lbl_confirm.pack(anchor="w", pady=(0, 5))

        self.entry_confirm = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Confirme a sua nova senha",
            height=45,
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA",
            text_color="#000000"
        )
        self.entry_confirm.pack(fill="x", pady=(0, 30))

        # Action Button
        self.btn_action = ctk.CTkButton(
            self.content_frame,
            text="alterar senha",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=10,
            fg_color="#1ABC9C", # Teal Color
            hover_color="#16A085"
        )
        self.btn_action.pack(fill="x")

if __name__ == "__main__":
    app = ChangePasswordApp()
    app.mainloop()