import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela Principal
        self.title("Coração em patas - Troque sua senha")
        self.geometry("1000x700")
        ctk.set_appearance_mode("Light")
        self.configure(fg_color="#F9F9F9") # Fundo da janela (off-white)

        # Cores e Fontes
        self.accent_color = "#8C52FF" # Roxo vibrante
        self.text_color_primary = "#000000"
        self.text_color_secondary = "#A0A0A0"
        self.font_title = ("Arial", 28, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_label = ("Arial", 14, "bold")
        self.font_brand = ("Arial", 16, "bold")

        # Card Principal (Container Branco)
        self.card_frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=30,
            width=900,
            height=700,
            border_width=0
        )
        self.card_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.card_frame.pack_propagate(False) # Respeitar tamanho fixo

        # --- Cabeçalho (Logo e Nome) ---
        self.header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=50, pady=40)

        # Ícone (Simulado com Frame Circular)
        self.logo_container = ctk.CTkFrame(
            self.header_frame,
            width=50,
            height=50,
            corner_radius=25,
            fg_color=self.accent_color
        )
        self.logo_container.pack(side="left")
        
        # Emoji de pata para simular o ícone
        self.logo_icon = ctk.CTkLabel(
            self.logo_container,
            text="🐾",
            text_color="white",
            font=("Arial", 24)
        )
        self.logo_icon.place(relx=0.5, rely=0.5, anchor="center")

        # Texto da Marca
        self.brand_label = ctk.CTkLabel(
            self.header_frame,
            text="Coração em patas",
            text_color=self.text_color_primary,
            font=self.font_brand
        )
        self.brand_label.pack(side="left", padx=15)

        # --- Conteúdo do Formulário (Centralizado) ---
        self.form_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.form_frame.pack(expand=True, fill="both", padx=150, pady=(0, 50))

        # Título
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="Altere sua senha",
            text_color=self.text_color_primary,
            font=self.font_title,
            anchor="w"
        )
        self.title_label.pack(fill="x", pady=(0, 5))

        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self.form_frame,
            text="Preencha seus dados para continuar",
            text_color=self.text_color_secondary,
            font=self.font_subtitle,
            anchor="w"
        )
        self.subtitle_label.pack(fill="x", pady=(0, 30))

        # Campo 1: Nome Completo
        self.label_nome = ctk.CTkLabel(
            self.form_frame,
            text="Nova senha",
            text_color=self.text_color_primary,
            font=self.font_label
            
        )
        self.label_nome.pack( pady=(0, 5))

        self.entry_nome = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="informe sua nova senha",
            height=45,
            width=450,
            corner_radius=12,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA",
            text_color="#333333",
            placeholder_text_color="#A0A0A0"
        )
        self.entry_nome.pack( pady=(0, 20))

        # Campo 2: Email
        self.label_email = ctk.CTkLabel(
            self.form_frame,
            text="confirmar nova senha",
            text_color=self.text_color_primary,
            font=self.font_label,
        )
        self.label_email.pack(pady=(0, 5))

        self.entry_email = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="confirme sua nova senha",
            height=45,
            width=450,
            corner_radius=12,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA",
            text_color="#333333",
            placeholder_text_color="#A0A0A0"
        )
        self.entry_email.pack(pady=(0, 30))

        # Botão Continuar
        self.btn_continuar = ctk.CTkButton(
            self.form_frame,
            text="Alterar senha",
            fg_color="#14B8A6",
            hover_color="#8C52FF",
            height=45,
            width=450,
            corner_radius=12,
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        self.btn_continuar.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()