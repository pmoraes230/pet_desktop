import customtkinter as ctk

class ModuloProntuario:
    def __init__(self, content_frame):
        self.content = content_frame

    def tela_prontuario(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(left_header, text="Prontuário eletrônico", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 10))

        self.search_pet_entry = ctk.CTkEntry(
            left_header,
            placeholder_text="🔍 Pesquise por tutor ou pet",
            height=45,
            width=400,
            corner_radius=22,
            border_color="#94A3B8"
        )
        self.search_pet_entry.pack(side="left")

        ctk.CTkButton(
            header,
            text="Salvar prontuário",
            fg_color="#A855F7",
            font=("Arial", 14, "bold"),
            width=180,
            height=45,
            corner_radius=10
        ).pack(side="right", anchor="n")

        corpo = ctk.CTkFrame(container, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=1)

        editor = ctk.CTkFrame(corpo, fg_color="transparent")
        editor.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        ctk.CTkLabel(editor, text="Anotações", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))

        txt = ctk.CTkTextbox(
            editor,
            corner_radius=20,
            border_width=1,
            border_color="#94A3B8",
            fg_color="#E5E7EB",
            text_color="black",
            font=("Arial", 13)
        )
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", "Digite aqui as observações...")

        hist = ctk.CTkFrame(corpo, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        hist.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(hist, text="Histórico Recente", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))

        scroll_h = ctk.CTkScrollableFrame(hist, fg_color="transparent")
        scroll_h.pack(fill="both", expand=True, padx=10, pady=15)

        self.criar_item_historico(scroll_h, "15 Jan 2026", "Vacinação")
        self.criar_item_historico(scroll_h, "02 Dez 2025", "Check-up Geral")

    def criar_item_historico(self, master, data, motivo):
        item = ctk.CTkFrame(master, fg_color="#F1F5F9", corner_radius=10)
        item.pack(fill="x", pady=5)
        ctk.CTkLabel(item, text=data, font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(item, text=motivo, font=("Arial", 11), text_color="#64748B").pack(anchor="w", padx=15, pady=(0, 10))