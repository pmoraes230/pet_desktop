import customtkinter as ctk
from datetime import datetime
from ..controllers.pet_controller import PetController

class ModuloPacientes:
    def __init__(self, content_frame, pet_controller: PetController):
        self.content = content_frame
        self.pet_controller = pet_controller

    def tela_pacientes(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # Cabeçalho
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold")).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Novo Paciente",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            width=150,
            corner_radius=10,
            command=self.abrir_popup_novo_paciente
        ).pack(side="right")

        # Campo de busca
        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 30))
        ctk.CTkEntry(
            search_row,
            placeholder_text="🔍 Pesquise por tutor ou pet",
            height=45,
            corner_radius=22
        ).pack(side="left", fill="x", expand=True, padx=(0, 15))

        # Grid de cards
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)
        grid.rowconfigure((0, 1, 2), weight=1)

        # Busca os pets reais do banco
        pets = self.pet_controller.listar_pets()

        for i, pet in enumerate(pets):
            # CHAVES CORRETAS do seu banco (conforme o print)
            id_pet = pet.get('id')
            nome = pet.get('NOME', 'Sem nome')
            especie   = pet.get('ESPECIE', '').lower()
            raca      = pet.get('RACA', 'Sem raça')
            data_nasc = pet.get('DATA_NASCIMENTO')
            sexo      = pet.get('SEXO', 'Não informado')
            castrado  = pet.get('CASTRADO', 'Não informado')
            peso      = pet.get('PESO') or '? kg'            # evita None

            idade     = self.calcular_idade(data_nasc)
            emoji     = "🐶" if "cachorro" in especie else "🐱" if "gato" in especie else "🐾"
            info      = f"{raca} • {idade} anos • {sexo}"

            # Cria o card e OBTÉM o frame retornado
            card = self.criar_card_paciente(
                grid,
                nome,
                info,
                emoji,
                peso,
                i // 3,   # linha
                i % 3,     # coluna
                id_pet,
                raca
            )

            # Tornar o card clicável sem sobrepor widgets — liga evento de clique ao frame
            def _abrir_perfil(event=None, pid=id_pet, n=nome, r=raca, e_emoji=emoji):
                self.tela_perfil_pet(pid, n, r, e_emoji)

            card.bind("<Button-1>", _abrir_perfil)
            # opcional: mudar cursor ao passar o mouse
            try:
                card.configure(cursor="hand2")
            except Exception:
                pass

    def calcular_idade(self, data_nasc):
        """Calcula idade em anos a partir da data de nascimento"""
        if not data_nasc:
            return "?"
        try:
            if isinstance(data_nasc, str):
                data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d")
            elif not isinstance(data_nasc, datetime):
                return "?"
            hoje = datetime.now()
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            return str(idade)
        except Exception:
            return "?"

    def criar_card_paciente(self, master, nome, info, icon, peso, row, col, id_pet, raca):
        """Card com botão para ver perfil"""
        card = ctk.CTkFrame(
            master,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # Força tamanho fixo (importante!)
        card.grid_propagate(False)
        card.configure(width=320, height=420)

        # Configura grid interno do card
        card.columnconfigure(0, weight=1)
        card.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Emoji
        emoji_lbl = ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 80)
        )
        emoji_lbl.grid(row=0, column=0, columnspan=3, pady=10, sticky="n")

        # Nome
        nome_lbl = ctk.CTkLabel(
            card,
            text=nome,
            font=("Arial", 20, "bold"),
            text_color="#000000"
        )
        nome_lbl.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")

        # Info
        info_lbl = ctk.CTkLabel(
            card,
            text=info,
            font=("Arial", 14),
            text_color="#64748B"
        )
        info_lbl.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

        # Peso
        peso_lbl = ctk.CTkLabel(
            card,
            text=f"Peso: {peso}",
            font=("Arial", 13),
            text_color="#94A3B8"
        )
        peso_lbl.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        # Botão Ver Perfil
        def abrir_perfil():
            self.tela_perfil_pet(id_pet, nome, raca, icon)

        btn_perfil = ctk.CTkButton(
            card,
            text="👁️ Ver Perfil",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            text_color="white",
            font=("Arial", 13, "bold"),
            corner_radius=10,
            height=40,
            command=abrir_perfil
        )
        btn_perfil.grid(row=4, column=0, columnspan=3, pady=15, padx=15, sticky="ew")

        return card
        

    def abrir_popup_novo_paciente(self):
        self.overlay = ctk.CTkFrame(self.content.master, fg_color="#1A1A1A") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.modal_frame = ctk.CTkFrame(self.overlay, width=400, height=520, corner_radius=20, 
                                       border_width=2, border_color="#14B8A6", fg_color="white")
        self.modal_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.modal_frame.pack_propagate(False)

        ctk.CTkLabel(self.modal_frame, text="🐾 Novo Paciente", font=("Arial", 22, "bold"), 
                     text_color="#14B8A6").pack(pady=20)

        form = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        def criar_input(label):
            ctk.CTkLabel(form, text=label, font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1")
            entry.pack(fill="x", pady=(2, 5))
            return entry

        criar_input("Nome do Pet")
        criar_input("Nome do Tutor")
        criar_input("Telefone de Contato")
        
        ctk.CTkLabel(form, text="Observações Iniciais", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1").pack(fill="x", pady=(2, 5))

        btn_container = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        btn_container.pack(fill="x", pady=25, padx=30)

        ctk.CTkButton(btn_container, text="Confirmar", fg_color="#14B8A6", width=160, height=40,
                      command=self.fechar_popup).pack(side="left", padx=5)
        ctk.CTkButton(btn_container, text="Cancelar", fg_color="#94A3B8", width=160, height=40,
                      command=self.fechar_popup).pack(side="right", padx=5)

    def fechar_popup(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()

    def tela_perfil_pet(self, id_pet, nome_pet, raca_pet, emoji):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=30)

        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)

        card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, 
                               width=350, border_width=1, border_color="#F1F5F9")
        card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))

        img_placeholder = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", height=220, corner_radius=30)
        img_placeholder.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(img_placeholder, text=emoji, font=("Arial", 80)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card_esq, text=nome_pet, font=("Arial", 32, "bold"), text_color="#1E293B").pack()
        ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Arial", 12, "bold"), text_color="#14B8A6").pack(pady=(0, 20))
        
        ctk.CTkLabel(card_esq, text=f"ID: {id_pet}", font=("Arial", 11), text_color="#94A3B8").pack(pady=(0, 10))

        tutor_box = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", corner_radius=15)
        tutor_box.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(tutor_box, text="TUTOR RESPONSÁVEL", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(tutor_box, text="Ana Souza", font=("Arial", 14, "bold"), text_color="#1E293B").pack(anchor="w", padx=15, pady=(0, 10))

        row_stats = ctk.CTkFrame(card_esq, fg_color="transparent")
        row_stats.pack(fill="x", padx=20, pady=20)
        
        p_box = ctk.CTkFrame(row_stats, fg_color="#F0FDFA", corner_radius=15, height=80)
        p_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(p_box, text="PESO", font=("Arial", 10, "bold"), text_color="#134E4A").pack(pady=(10, 0))
        ctk.CTkLabel(p_box, text="12 kg", font=("Arial", 18, "bold"), text_color="#134E4A").pack()

        s_box = ctk.CTkFrame(row_stats, fg_color="#EFF6FF", corner_radius=15, height=80)
        s_box.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(s_box, text="SEXO", font=("Arial", 10, "bold"), text_color="#1E3A8A").pack(pady=(10, 0))
        ctk.CTkLabel(s_box, text="Macho", font=("Arial", 18, "bold"), text_color="#1E3A8A").pack()

        prox_c = ctk.CTkFrame(card_esq, fg_color="#14B8A6", corner_radius=30)
        prox_c.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(prox_c, text="proxima consulta: 15 de Fev", font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", padx=20)

        self.right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=40, 
                                     border_width=1, border_color="#F1F5F9")
        self.right_col.grid(row=0, column=1, sticky="nsew")

        tab_header = ctk.CTkFrame(self.right_col, fg_color="#F1F5F9", corner_radius=25, height=50)
        tab_header.pack(pady=30, padx=30, anchor="w")

        self.btn_sobre = ctk.CTkButton(
            tab_header, text="SOBRE", width=120, corner_radius=25,
            fg_color="#14B8A6", text_color="white",
            command=lambda: self.mudar_aba_pet("sobre")
        )
        self.btn_sobre.pack(side="left", padx=2, pady=2)

        self.btn_saude = ctk.CTkButton(
            tab_header, text="SAÚDE", width=120, corner_radius=25,
            fg_color="transparent", text_color="#64748B",
            command=lambda: self.mudar_aba_pet("saude")
        )
        self.btn_saude.pack(side="left", padx=2, pady=2)

        self.container_abas = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.container_abas.pack(fill="both", expand=True, padx=40)

        self.mudar_aba_pet("sobre")

    def mudar_aba_pet(self, aba):
        for w in self.container_abas.winfo_children():
            w.destroy()

        if aba == "sobre":
            self.btn_sobre.configure(fg_color="#14B8A6", text_color="white")
            self.btn_saude.configure(fg_color="transparent", text_color="#64748B")

            # Título
            ctk.CTkLabel(
                self.container_abas,
                text="Sobre o pet:",
                font=("Arial", 18, "bold"),
                text_color="#1E293B"
            ).pack(anchor="w", pady=(10, 5))

            # Texto descritivo
            desc = ctk.CTkLabel(
                self.container_abas,
                text="Pet dócil, porém agitado. Gosta de brincar e é muito apegado ao tutor.",
                font=("Arial", 14),
                text_color="#334155",
                wraplength=600,
                justify="left"
            )
            desc.pack(anchor="w", pady=(0, 20))

            # Título personalidade
            ctk.CTkLabel(
                self.container_abas,
                text="Personalidade",
                font=("Arial", 16, "bold"),
                text_color="#1E293B"
            ).pack(anchor="w", pady=(0, 10))

            # Container das tags
            tags_frame = ctk.CTkFrame(self.container_abas, fg_color="transparent")
            tags_frame.pack(anchor="w")

            def criar_tag(master, texto):
                tag = ctk.CTkFrame(master, fg_color="#FEF3C7", corner_radius=20, height=35)
                tag.pack(side="left", padx=5)
                ctk.CTkLabel(
                    tag,
                    text=texto,
                    font=("Arial", 12, "bold"),
                    text_color="#92400E"
                ).pack(padx=15, pady=5)

            # Exemplo de tags
            criar_tag(tags_frame, "Brincalhão")
            criar_tag(tags_frame, "Protetor")
            criar_tag(tags_frame, "Guloso")


        else:
            self.btn_saude.configure(fg_color="#14B8A6", text_color="white")
            self.btn_sobre.configure(fg_color="transparent", text_color="#64748B")
            
            vacinas = [("V10", "10/01/2026", "10/01/2027"), ("Raiva", "15/12/2025", "15/12/2026")]
            for n, d, p in vacinas:
                v_card = ctk.CTkFrame(self.container_abas, fg_color="white", 
                                     corner_radius=25, border_width=1, border_color="#F1F5F9")
                v_card.pack(fill="x", pady=10)
                ctk.CTkLabel(v_card, text=f"{n}\nAplicada: {d}", font=("Arial", 13, "bold"),
                             justify="left").pack(side="left", padx=20)