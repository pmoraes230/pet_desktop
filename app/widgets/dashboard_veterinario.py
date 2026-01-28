import customtkinter as ctk

class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Configuração da malha (Grid)
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) # Linha da Topbar
        self.grid_rowconfigure(1, weight=1) # Linha do Conteúdo

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color="#14B8A6", width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # LOGO
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=20, padx=10, fill="x")
        
        self.logo_circle = ctk.CTkLabel(self.logo_frame, text="🐾", font=("Arial", 20), width=45, height=45, fg_color="#8B5CF6", text_color="white", corner_radius=22)
        self.logo_circle.pack(side="left", padx=(10, 5))
        
        self.logo_text = ctk.CTkLabel(self.logo_frame, text="Coração em patas", font=("Arial", 15, "bold"), text_color="black")
        self.logo_text.pack(side="left")

        # --- TOPBAR (Estilizada e Funcional) ---
        self.topbar = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        self.topbar.grid(row=0, column=1, sticky="ew")
        self.topbar.grid_propagate(False)

        self.linha_separadora = ctk.CTkFrame(self, fg_color="#E2E8F0", height=2)
        self.linha_separadora.grid(row=0, column=1, sticky="s")

        ctk.CTkLabel(self.topbar, text="Bom dia, Usuário!", font=("Arial", 16, "bold"), text_color="black").pack(side="left", padx=30)

        self.right_info = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.right_info.pack(side="right", padx=20)

        ctk.CTkLabel(self.right_info, text="🔔", font=("Arial", 20), cursor="hand2").pack(side="left", padx=15)

        self.avatar = ctk.CTkLabel(self.right_info, text="U", font=("Arial", 14, "bold"), width=38, height=38, fg_color="#A855F7", text_color="white", corner_radius=19)
        self.avatar.pack(side="left")

        # --- ÁREA DE CONTEÚDO ---
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")

        # BOTÕES DO MENU (Voltaram ao estilo original)
        self.criar_botao("Dashboard", self.tela_dashboard)
        self.criar_botao("Mensagens", self.tela_mensagens)
        self.criar_botao("Pacientes", self.tela_pacientes)
        self.criar_botao("Agenda", self.tela_agenda)
        self.criar_botao("Prontuários", self.tela_prontuarios)
        self.criar_botao("Financeiro", self.tela_financeiro)

        self.tela_dashboard()

    # FUNÇÕES DE LÓGICA
    def trocar_tela(self, func):
        for widget in self.content.winfo_children():
            widget.destroy()
        func()

    def criar_botao(self, texto, comando):
        # Removido o 'anchor="w"' e 'fg_color="transparent"' para voltar como era antes
        ctk.CTkButton(
            self.sidebar,
            text=texto,
            fg_color="#14B8A6",
            hover_color="#188C7F",
            text_color="white",
            font=("Arial", 16),
            height=45,
            command=lambda: self.trocar_tela(comando)
        ).pack(fill="x", padx=20, pady=6)

    # TELAS
    def tela_dashboard(self):
        # Container Principal com scroll se necessário
        scroll_container = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll_container, text="Painel de Controle", font=("Arial", 24, "bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 20))

        # --- CARDS DE STATUS ---
        cards_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        
        # Grid para 3 cards
        cards_frame.columnconfigure((0, 1, 2), weight=1, pad=20)

        self.criar_card_info(cards_frame, "Pacientes Totais", "1,250", "#8B5CF6", 0)
        self.criar_card_info(cards_frame, "Consultas Hoje", "12", "#14B8A6", 1)
        self.criar_card_info(cards_frame, "Receita Mensal", "R$ 8.450", "#F59E0B", 2)

        # --- SEÇÃO DE PRÓXIMAS CONSULTAS ---
        ctk.CTkLabel(scroll_container, text="Próximas Consultas do Dia", font=("Arial", 18, "bold"), text_color="#1e293b").pack(anchor="w", pady=(30, 10))
        
        # Simulando uma lista de tarefas/consultas
        consultas = [
            ("09:00", "Rex (Labrador)", "Vacinação"),
            ("10:30", "Luna (Gato)", "Check-up"),
            ("14:00", "Thor (Pug)", "Cirurgia"),
        ]

        for hora, pet, servico in consultas:
            item = ctk.CTkFrame(scroll_container, fg_color="white", height=60, corner_radius=10)
            item.pack(fill="x", pady=5)
            ctk.CTkLabel(item, text=hora, font=("Arial", 14, "bold"), text_color="#14B8A6").pack(side="left", padx=20)
            ctk.CTkLabel(item, text=f"{pet} - {servico}", font=("Arial", 14), text_color="#475569").pack(side="left", padx=10)
            ctk.CTkButton(item, text="Ver Detalhes", width=100, height=30, fg_color="#F1F5F9", text_color="#1e293b", hover_color="#E2E8F0").pack(side="right", padx=20)

    def criar_card_info(self, master, titulo, valor, cor, coluna):
        card = ctk.CTkFrame(master, fg_color="white", height=120, corner_radius=15, border_width=1, border_color="#E2E8F0")
        card.grid(row=0, column=coluna, sticky="nsew", padx=10)
        card.grid_propagate(False)
        
        ctk.CTkLabel(card, text=titulo, font=("Arial", 14), text_color="#64748b").pack(pady=(15, 0))
        ctk.CTkLabel(card, text=valor, font=("Arial", 28, "bold"), text_color=cor).pack(pady=(5, 0))


    def tela_mensagens(self):
        ctk.CTkLabel(self.content, text="Mensagens", font=("Arial", 26, "bold")).pack(pady=20)

    def tela_pacientes(self):
        # Topo: Busca e Botão Adicionar
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(header, text="Gestão de Pacientes", font=("Arial", 24, "bold"), text_color="#1e293b").pack(side="left")
        
        ctk.CTkButton(header, text="+ Novo Paciente", fg_color="#8B5CF6", hover_color="#7C3AED", font=("Arial", 14, "bold")).pack(side="right")
        
        # Barra de Pesquisa
        search_frame = ctk.CTkFrame(self.content, fg_color="white", height=50)
        search_frame.pack(fill="x", padx=30, pady=10)
        
        entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar por nome do pet ou dono...", width=400, border_width=0, fg_color="transparent")
        entry_search.pack(side="left", padx=10, pady=10)

        # Listagem (Tabela Fake)
        scroll_list = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll_list.pack(fill="both", expand=True, padx=30, pady=10)

        # Cabeçalho da Tabela
        tab_head = ctk.CTkFrame(scroll_list, fg_color="#F1F5F9", height=40)
        tab_head.pack(fill="x", pady=5)
        ctk.CTkLabel(tab_head, text="NOME DO PET", font=("Arial", 12, "bold"), text_color="#64748b").pack(side="left", padx=20)
        ctk.CTkLabel(tab_head, text="ESPÉCIE", font=("Arial", 12, "bold"), text_color="#64748b").pack(side="left", padx=100)
        ctk.CTkLabel(tab_head, text="PROPRIETÁRIO", font=("Arial", 12, "bold"), text_color="#64748b").pack(side="left", padx=100)

        # Exemplo de linha de paciente
        for _ in range(10): # Simulando vários dados
            row = ctk.CTkFrame(scroll_list, fg_color="white", height=50)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text="Mel", font=("Arial", 14), text_color="black").place(x=20, y=10)
            ctk.CTkLabel(row, text="Canino (Golden)", font=("Arial", 14), text_color="black").place(x=185, y=10)
            ctk.CTkLabel(row, text="Mariana Silva", font=("Arial", 14), text_color="black").place(x=385, y=10)
            ctk.CTkButton(row, text="Editar", width=60, fg_color="#14B8A6").pack(side="right", padx=10, pady=10)

    def tela_agenda(self):
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(container, text="Agenda de Consultas", font=("Arial", 26, "bold"), text_color="#1e293b").pack(anchor="w")

        # Aqui você poderia integrar um calendário, mas vamos fazer uma lista de horários
        horarios = ["08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00"]
        
        scroll_agenda = ctk.CTkScrollableFrame(container, fg_color="white", corner_radius=15)
        scroll_agenda.pack(fill="both", expand=True, pady=20)

        for hr in horarios:
            linha = ctk.CTkFrame(scroll_agenda, fg_color="transparent")
            linha.pack(fill="x", pady=10)
            
            ctk.CTkLabel(linha, text=hr, font=("Arial", 16, "bold"), text_color="#64748b").pack(side="left", padx=20)
            
            # Separador visual
            ctk.CTkFrame(linha, width=2, fg_color="#E2E8F0", height=40).pack(side="left", padx=10)
            
            # Slot de consulta (exemplo de slot vazio vs ocupado)
            if hr == "09:00":
                btn = ctk.CTkButton(linha, text="Consulta: Pipoca (Gato) - Vacina", fg_color="#8B5CF6", hover_color="#7C3AED", anchor="w")
                btn.pack(side="left", fill="x", expand=True, padx=10)
            else:
                btn = ctk.CTkButton(linha, text="+ Reservar Horário", fg_color="transparent", text_color="#94A3B8", border_width=1, border_color="#E2E8F0", hover_color="#F8FAFC")
                btn.pack(side="left", fill="x", expand=True, padx=10)

    def tela_prontuarios(self):
        ctk.CTkLabel(self.content, text="Prontuários", font=("Arial", 26, "bold")).pack(pady=20)

    def tela_financeiro(self):
        main_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Topo
        ctk.CTkLabel(main_frame, text="Financeiro", font=("Arial", 26, "bold"), text_color="#1e293b").pack(anchor="w")

        # Cards de Balanço
        balance_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        balance_frame.pack(fill="x", pady=20)
        balance_frame.columnconfigure((0, 1), weight=1)

        # Card Entradas
        card_in = ctk.CTkFrame(balance_frame, fg_color="#DCFCE7", height=100)
        card_in.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(card_in, text="Total Recebido (Mês)", text_color="#166534").pack(pady=(15, 0))
        ctk.CTkLabel(card_in, text="R$ 12.400,00", font=("Arial", 22, "bold"), text_color="#166534").pack()

        # Card Saídas
        card_out = ctk.CTkFrame(balance_frame, fg_color="#FEE2E2", height=100)
        card_out.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        ctk.CTkLabel(card_out, text="Total Despesas (Mês)", text_color="#991B1B").pack(pady=(15, 0))
        ctk.CTkLabel(card_out, text="R$ 3.950,00", font=("Arial", 22, "bold"), text_color="#991B1B").pack()

        # Botão de Relatório
        ctk.CTkButton(main_frame, text="Gerar Relatório PDF", fg_color="#1e293b").pack(pady=20)