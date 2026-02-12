import customtkinter as ctk
from datetime import datetime

class ModuloProntuario:
    def __init__(self, content_frame, prontuario_controller):
        self.content = content_frame
        self.controller = prontuario_controller
        self.pets_map = {}

    def tela_prontuario(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)

        # HEADER
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_header,
            text="Prontuário eletrônico",
            font=("Arial", 32, "bold")
        ).pack(anchor="w", pady=(0, 10))

        linha_paciente = ctk.CTkFrame(left_header, fg_color="transparent")
        linha_paciente.pack(anchor="w")

        ctk.CTkLabel(
            linha_paciente,
            text="PACIENTE:",
            font=("Arial", 12, "bold"),
            text_color="#64748B"
        ).pack(side="left", padx=(0, 8))

        self.combo_paciente = ctk.CTkOptionMenu(
            linha_paciente,
            values=["Carregando..."],
            command=self.on_pet_selecionado
        )
        self.combo_paciente.pack(side="left")

        self.btn_salvar = ctk.CTkButton(
            header,
            text="Salvar prontuário",
            fg_color="#A855F7",
            hover_color="#9333EA",
            font=("Arial", 14, "bold"),
            width=200,
            height=50,
            corner_radius=25,
            command=self.salvar_prontuario
        )
        self.btn_salvar.pack(side="right", anchor="n")

        # CORPO
        corpo = ctk.CTkFrame(container, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=1)

        # Editor
        editor = ctk.CTkFrame(corpo, fg_color="transparent")
        editor.grid(row=0, column=0, sticky="nsew", padx=(0, 25))

        self.txt = ctk.CTkTextbox(
            editor,
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0",
            fg_color="#F8FAFC",
            text_color="black",
            font=("Arial", 14)
        )
        self.txt.pack(fill="both", expand=True)

        # Histórico
        self.hist = ctk.CTkScrollableFrame(
            corpo,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.hist.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.hist,
            text="Histórico",
            font=("Arial", 18, "bold")
        ).pack(pady=(20, 10))

        # Carregar pets
        self.carregar_pets()

    # =========================
    # FUNÇÕES
    # =========================

    def carregar_pets(self):
        pets = self.controller.listar_pets()

        nomes = []
        for pet in pets:
            pet_id = pet.get('id')
            nome = pet.get('NOME', 'Sem nome')
            nomes.append(nome)
            self.pets_map[nome] = pet_id

        if not nomes:
            nomes = ["Nenhum paciente"]

        self.combo_paciente.configure(values=nomes)
        self.combo_paciente.set(nomes[0])

    def on_pet_selecionado(self, nome_pet):
        pet_id = self.pets_map.get(nome_pet)
        if not pet_id:
            return

        for widget in self.hist.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        historico = self.controller.historico(pet_id)

        if not historico:
            ctk.CTkLabel(
                self.hist,
                text="Nenhum registro anterior.",
                text_color="#94A3B8"
            ).pack(pady=20)
            return

        for registro in historico:
            data = registro.get('DATA_CONSULTA')
            texto = registro.get('OBSERVACOES') or ''
            
            # Converter string para datetime se necessário
            if isinstance(data, str):
                try:
                    from datetime import datetime
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                    data_str = data.strftime("%d %b %Y")
                except:
                    data_str = data
            else:
                data_str = data.strftime("%d %b %Y") if hasattr(data, 'strftime') else str(data)

            item = ctk.CTkFrame(self.hist, fg_color="#F1F5F9", corner_radius=10)
            item.pack(fill="x", pady=5, padx=10)

            ctk.CTkLabel(item, text=data_str, font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            ctk.CTkLabel(item, text=texto[:60] + "...", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(0, 10))

    def salvar_prontuario(self):
        nome_pet = self.combo_paciente.get()
        pet_id = self.pets_map.get(nome_pet)

        if not pet_id:
            return

        texto = self.txt.get("1.0", "end").strip()
        if not texto:
            return

        self.controller.salvar(pet_id, texto)
        self.txt.delete("1.0", "end")
        self.on_pet_selecionado(nome_pet)
