import customtkinter as ctk

class ModuloChat:
    def tela_chat(self):
        chat_container = ctk.CTkFrame(self.content, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        chat_container.columnconfigure(0, weight=1); chat_container.columnconfigure(1, weight=3); chat_container.rowconfigure(0, weight=1)

        contatos_frame = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        contatos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(contatos_frame, text="Conversas", font=("Arial", 20, "bold")).pack(anchor="w", padx=25, pady=20)
        scroll_contatos = ctk.CTkScrollableFrame(contatos_frame, fg_color="transparent"); scroll_contatos.pack(fill="both", expand=True, padx=10)
        self.criar_item_contato(scroll_contatos, "Ana (Tutor)", "🐶", True)
        self.criar_item_contato(scroll_contatos, "Carlos (Tutor)", "🐱")

        janela_chat = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0"); janela_chat.grid(row=0, column=1, sticky="nsew")
        header = ctk.CTkFrame(janela_chat, fg_color="transparent", height=60); header.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(header, text="Conversando com Ana", font=("Arial", 16, "bold")).pack(side="left")
        self.area_msg = ctk.CTkScrollableFrame(janela_chat, fg_color="#F8FAFC", corner_radius=0); self.area_msg.pack(fill="both", expand=True)
        self.criar_bolha_mensagem(self.area_msg, "Olá Dr., a Paçoca está bem?", "09:41", "tutor")
        self.criar_bolha_mensagem(self.area_msg, "Olá! Sim, ela está ótima.", "09:45", "vet")
        input_f = ctk.CTkFrame(janela_chat, fg_color="white", height=80); input_f.pack(fill="x", side="bottom", padx=20, pady=20)
        ctk.CTkEntry(input_f, placeholder_text="Digite sua mensagem...", height=50, corner_radius=25).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(input_f, text="➤", width=50, height=50, corner_radius=25, fg_color="#A855F7").pack(side="right")

    def criar_item_contato(self, master, nome, avatar, sel=False):
        btn = ctk.CTkButton(master, text=f"{avatar}  {nome}", fg_color="#F3E8FF" if sel else "transparent", 
                            text_color="black", hover_color="#F8FAFC", anchor="w", height=60, corner_radius=15)
        btn.pack(fill="x", pady=2)

    def criar_bolha_mensagem(self, master, texto, hora, tipo):
        side = "right" if tipo == "vet" else "left"
        cor = "#9333EA" if tipo == "vet" else "white"
        txt_cor = "white" if tipo == "vet" else "black"
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(fill="x", padx=15, pady=5)
        bolha = ctk.CTkFrame(f, fg_color=cor, corner_radius=15, border_width=1 if tipo=="tutor" else 0, border_color="#E2E8F0")
        bolha.pack(side=side)
        ctk.CTkLabel(bolha, text=texto, text_color=txt_cor, wraplength=250, justify="left").pack(padx=15, pady=10)
        ctk.CTkLabel(f, text=hora, font=("Arial", 9), text_color="#94A3B8").pack(side=side, padx=5)