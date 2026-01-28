import customtkinter as ctk

# Configuração inicial do tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class VerificationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela Principal
        self.title("Coração em patas - Verificação")
        self.geometry("1000x700")
        self.configure(fg_color="#F3F4F6")  # Fundo cinza claro da janela

        # --- Card Central ---
        # Cria um container branco centralizado
        self.card_frame = ctk.CTkFrame(
            self, 
            fg_color="white", 
            corner_radius=30, 
            width=800, 
            height=600,
            border_color="#E5E7EB",
            border_width=1
        )
        self.card_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.card_frame.pack_propagate(False) # Garante que o frame mantenha o tamanho definido

        # --- Cabeçalho (Logo e Nome) ---
        self.header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=50, pady=40)

        # Simulação do Logo (Círculo Roxo com Ícone)
        self.logo_circle = ctk.CTkLabel(
            self.header_frame, 
            text="🐾",  # Emoji para simular a pata
            font=("Arial", 24), 
            width=50, 
            height=50, 
            fg_color="#8B5CF6", # Roxo vibrante
            text_color="white", 
            corner_radius=25  # Torna o label circular
        )
        self.logo_circle.pack(side="left")

        # Nome da Marca
        self.brand_label = ctk.CTkLabel(
            self.header_frame, 
            text="Coração em patas", 
            font=("Arial", 16, "bold"), 
            text_color="black"
        )
        self.brand_label.pack(side="left", padx=15)

        # --- Conteúdo Central (Formulário) ---
        self.content_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both")

        # Título
        self.title_label = ctk.CTkLabel(
            self.content_frame, 
            text="Insira o código", 
            font=("Arial", 32, "bold"), 
            text_color="black"
        )
        self.title_label.pack(pady=(20, 10))

        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame, 
            text="Enviamos um código para o seu e-mail, insira-o para\ncontinuar", 
            font=("Arial", 14), 
            text_color="#111827",  # Preto suave
            justify="center"
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Inputs do Código (5 caixas)
        self.input_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.input_container.pack(pady=(0, 15))

        self.code_entries = []
        for i in range(5):
            entry = ctk.CTkEntry(
                self.input_container, 
                width=60, 
                height=60, 
                corner_radius=15, 
                border_width=2, 
                border_color="#E5E7EB",
                fg_color="white",
                text_color="black",
                font=("Arial", 24, "bold"),
                justify="center"
            )
            entry.grid(row=0, column=i, padx=10)
            self.code_entries.append(entry)

        # Link Reenviar Código
        self.resend_label = ctk.CTkLabel(
            self.content_frame, 
            text="Reenviar código", 
            font=("Arial", 12), 
            text_color="#9CA3AF", # Cinza
            cursor="hand2"
        )
        self.resend_label.pack(pady=(0, 30))

        # Botão Enviar
        self.submit_btn = ctk.CTkButton(
            self.content_frame, 
            text="Enviar", 
            font=("Arial", 14, "bold"), 
            height=50, 
            width=380, 
            fg_color="#14B8A6", # Verde do botão
            hover_color="#7C3AED",
            corner_radius=10
        )
        self.submit_btn.pack(pady=(0, 30))

        # Texto de Rodapé (Spam)
        self.footer_label = ctk.CTkLabel(
            self.content_frame, 
            text="Caso não encontre o e-mail na sua caixa de\nentrada, verifique a pasta de spam!", 
            font=("Arial", 12), 
            text_color="#9CA3AF", # Cinza claro
            justify="center"
        )
        self.footer_label.pack()

if __name__ == "__main__":
    app = VerificationApp()
    app.mainloop()