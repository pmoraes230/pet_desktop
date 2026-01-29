import customtkinter as ctk

class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # --- CONFIGURAÇÃO DE COLUNAS/LINHAS ---
        self.grid_columnconfigure(0, weight=0) # Coluna da Sidebar (fixa)
        self.grid_columnconfigure(1, weight=1) # Coluna do Conteúdo (expande)

        # Agora a linha 0 é SÓ da Topbar e a linha 1 é do resto
        self.grid_rowconfigure(0, weight=0, minsize=70) # Altura da Topbar
        self.grid_rowconfigure(1, weight=1)             # Altura da Sidebar e Conteúdo

        # --- TOPBAR (De ponta a ponta) ---
        self.topbar = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        # columnspan=2 faz ela ocupar a largura da sidebar + a largura do conteúdo
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew") 
        self.topbar.grid_propagate(False)

        # Elementos da Topbar (Mantidos)
        ctk.CTkLabel(self.topbar, text="Bom dia, Usuário!", font=("Arial", 16, "bold"), text_color="black").pack(side="left", padx=30)
        self.right_info = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.right_info.pack(side="right", padx=20)
        ctk.CTkLabel(self.right_info, text="🔔", font=("Arial", 20), cursor="hand2").pack(side="left", padx=15)
        self.avatar = ctk.CTkLabel(self.right_info, text="U", font=("Arial", 14, "bold"), width=38, height=38, fg_color="#A855F7", text_color="white", corner_radius=19)
        self.avatar.pack(side="left")

        # Linha Separadora (agora embaixo da topbar inteira)
        self.linha_separadora = ctk.CTkFrame(self, fg_color="#E2E8F0", height=2)
        self.linha_separadora.grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- SIDEBAR (Abaixo da Topbar) ---
        # Note que agora o row=1 e não tem mais rowspan=2
        self.sidebar = ctk.CTkFrame(self, fg_color="#14B8A6", width=260, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew") 
        self.sidebar.grid_propagate(False)


        # LOGO (Dentro da Sidebar)
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=20, padx=10, fill="x")

        # Criamos um FRAME para ser o círculo perfeito
        self.logo_circle = ctk.CTkFrame(
            self.logo_frame, 
            width=44,            # Largura
            height=44,           # Altura igual
            corner_radius=22,    # Metade exata
            fg_color="#8B5CF6"
        )
        self.logo_circle.pack(side="left", padx=(10, 5))
        self.logo_circle.pack_propagate(False) # Impede que o frame mude de tamanho por causa do texto

        # Colocamos o emoji centralizado dentro do círculo usando 'place'
        self.emoji_label = ctk.CTkLabel(
            self.logo_circle, 
            text="🐾", 
            font=("Arial", 20),
            text_color="white"
        )
        self.emoji_label.place(relx=0.5, rely=0.5, anchor="center") # Centralização absoluta

        # Texto da Logo
        self.logo_text = ctk.CTkLabel(
            self.logo_frame, 
            text="Coração em patas", 
            font=("Arial", 15, "bold"), 
            text_color="black"
        )
        self.logo_text.pack(side="left", padx=5)
        # --- ÁREA DE CONTEÚDO ---
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0, height=500)
        self.content.grid(row=1, column=1, sticky="nsew")

        # Botões do Menu
        self.criar_botao_sidebar("Dashboard", self.tela_dashboard)
        self.criar_botao_sidebar("Pacientes", self.tela_pacientes)
        self.criar_botao_sidebar("Prontuário", self.tela_prontuario)
        self.criar_botao_sidebar("Agenda", self.tela_agenda)
        self.criar_botao_sidebar("Financeiro", self.tela_financeiro)
        
        

        self.tela_dashboard()

    # --- LÓGICA DE NAVEGAÇÃO ---
    def criar_botao_sidebar(self, texto, comando):
        ctk.CTkButton(self.sidebar, text=texto, fg_color="#14B8A6", hover_color="#188C7F", 
                      text_color="white", font=("Arial", 16), height=45, 
                      command=lambda: self.trocar_tela(comando)).pack(fill="x", padx=20, pady=6)

    def trocar_tela(self, func):
        for widget in self.content.winfo_children():
            widget.destroy()
        func()

    # --- TELA 1: DASHBOARD ---
    def tela_dashboard(self):
        # Container principal (Scrollable)
        # Aumentei o padding para dar "ar" ao layout
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)

        # --- SEÇÃO DE MÉTRICAS (Cards de cima) ---
        metrics = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 30))
        
        # Garantir que as 3 colunas de métricas sejam iguais
        metrics.columnconfigure((0, 1, 2), weight=1, uniform="equal")

        self.criar_card_metrica(metrics, "1,240", "Total Pacientes", "🟦", "+12%", 0)
        self.criar_card_metrica(metrics, "8", "Consultas hoje", "🟩", None, 1)
        self.criar_card_metrica(metrics, "4.2K", "Faturamento mês", "🟨", None, 2)

        # --- GRID PRINCIPAL (Histórico e Alertas) ---
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        
        # Configuração de pesos: Coluna 0 (60%), Coluna 1 (40%)
        main_grid.columnconfigure(0, weight=3) 
        main_grid.columnconfigure(1, weight=2) 
        main_grid.rowconfigure(0, weight=1) # Importante para alinhar a altura das duas colunas

        # --- LADO ESQUERDO: Histórico ---
        left_container = ctk.CTkFrame(main_grid, fg_color="transparent")
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(left_container, text="Histórico Recente", 
                    font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", pady=(0, 15))
        
        # O card branco que segura o histórico
        hist_card = ctk.CTkFrame(left_container, fg_color="white", corner_radius=20, 
                                border_width=1, border_color="#E2E8F0")
        hist_card.pack(fill="both", expand=True, ipady=10) # ipady dá um respiro interno
        
        self.criar_linha_agendamento(hist_card, "09:00 AM", "Paçoca", "Vacinação Anual", "Confirmado", "#DCFCE7", "#166534")
        self.criar_linha_agendamento(hist_card, "10:30 AM", "Luna", "Avaliação", "Aguardando", "#FEF9C3", "#854D0E")
        self.criar_linha_agendamento(hist_card, "11:00 AM", "Thor", "Retorno", "Confirmado", "#DCFCE7", "#166534")

        # --- LADO DIREITO: Alertas ---
        right_container = ctk.CTkFrame(main_grid, fg_color="transparent")
        right_container.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(right_container, text="Alertas de saúde", 
                    font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", pady=(0, 15))
        
        # Card de Alerta
        al_card = ctk.CTkFrame(right_container, fg_color="white", corner_radius=20, 
                            border_width=1, border_color="#E2E8F0")
        al_card.pack(fill="both", expand=True, padx=2) # fill="both" para alinhar altura com o da esquerda
        
        # Conteúdo interno do alerta
        self.criar_item_alerta(al_card, "Bob (Golden)", "Queda brusca de peso registrada.")
        self.criar_item_alerta(al_card, "Mel (Poodle)", "Vacina de Raiva vence em 3 dias.")

    # --- TELA 2: PACIENTES ---
    def tela_pacientes(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(header, text="+ Novo Paciente", fg_color="#14B8A6", width=150, corner_radius=10).pack(side="right")

        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 30))
        search_entry = ctk.CTkEntry(search_row, placeholder_text="🔍 Pesquise por tutor ou pet", height=45, corner_radius=22)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)
        
        self.criar_card_paciente(grid, "Paçoca", "Saudável", "Vira-lata • 4 Anos", "🐶", 0)
        self.criar_card_paciente(grid, "Luna", "Saudável", "Siamês • 2 Anos", "🐱", 1)
        self.criar_card_paciente(grid, "Thor", "Saudável", "Bulldog • 3 Anos", "🐶", 2)

    # --- TELA 3: AGENDA (CORRIGIDA) ---
    def tela_agenda(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Agendamentos", font=("Arial", 24, "bold"), text_color="black").pack(side="left")
        
        # Badge corrigida: CTKLabel não aceita border_width. Usamos Frame em volta.
        badge_frame = ctk.CTkFrame(header, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        badge_frame.pack(side="right")
        ctk.CTkLabel(badge_frame, text="Fevereiro 2026", font=("Arial", 14, "bold"), text_color="black").pack(padx=20, pady=5)

        dias_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        dias_frame.pack(fill="x", pady=(0, 30))
        dias_frame.columnconfigure((0,1,2,3,4,5,6), weight=1)
        
        dias = [("seg", "10"), ("ter", "11"), ("qua", "12"), ("qui", "13"), ("sex", "14"), ("sáb", "15"), ("dom", "16")]
        for i, (nome, num) in enumerate(dias):
            d_card = ctk.CTkFrame(dias_frame, fg_color="transparent")
            d_card.grid(row=0, column=i, pady=20)
            ctk.CTkLabel(d_card, text=nome, font=("Arial", 13), text_color="#64748B").pack()
            ctk.CTkLabel(d_card, text=num, font=("Arial", 16, "bold"), text_color="black").pack()

        consultas = [("08:00", "09:00", "Vacinação: Paçoca", "Dr. Silva . Sala 03"), ("09:00", "10:30", "Raio-X: Thor", "Dr. Helena . Sala 03")]
        for hf, hp, tit, det in consultas:
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=10)
            ctk.CTkLabel(r, text=hf, font=("Arial", 16, "bold"), width=80).pack(side="left", padx=(0, 20))
            self.criar_card_agendamento_detalhado(r, hp, tit, det)

    # --- TELA 4: FINANCEIRO ---
    def tela_financeiro(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        ctk.CTkLabel(scroll, text="Painel Financeiro", font=("Arial", 24, "bold"), text_color="black").pack(anchor="w", pady=(0, 25))

        metrics = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 30))
        metrics.columnconfigure((0, 1, 2), weight=1)
        self.criar_card_fin_topo(metrics, "Entrada (Mês)", "R$ 14.500", 0)
        self.criar_card_fin_topo(metrics, "Saídas (Mês)", "R$ 5.230", 1)
        self.criar_card_fin_topo(metrics, "Saldo Líquido", "R$ 9.230", 2)

        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=2)
        main_grid.columnconfigure(1, weight=1)

        chart = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0", height=300)
        chart.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        ctk.CTkLabel(chart, text="Fluxo de Caixa Semestral", font=("Arial", 18, "bold")).pack(pady=15)

        trans = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        trans.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(trans, text="Transações Recentes", font=("Arial", 18, "bold")).pack(pady=15)
        for _ in range(3): 
            self.criar_item_transacao(trans, "Pagamento: Paçoca", "Hoje, 14:30", "+ R$ 150,00")

    # --- MÉTODOS AUXILIARES ---
    def criar_card_metrica(self, master, valor, titulo, icon, badge, col):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0", height=140)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=icon, font=("Arial", 24)).pack(anchor="w", padx=25, pady=(20, 0))
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=25)
        ctk.CTkLabel(f, text=valor, font=("Arial", 28, "bold")).pack(side="left")
        if badge: ctk.CTkLabel(f, text=badge, text_color="#22C55E", font=("Arial", 12, "bold")).pack(side="right")
        ctk.CTkLabel(card, text=titulo, text_color="#64748B", font=("Arial", 13)).pack(anchor="w", padx=25)

    def criar_linha_agendamento(self, master, hora, pet, info, status, bg, txt):
        l = ctk.CTkFrame(master, fg_color="transparent", height=80)
        l.pack(fill="x", padx=15)
        ctk.CTkLabel(l, text=hora, font=("Arial", 12, "bold"), width=70).pack(side="left")
        ctk.CTkLabel(l, text="🐶", font=("Arial", 20), fg_color="#F1F5F9", width=45, height=45, corner_radius=22).pack(side="left", padx=10, pady=15)
        t = ctk.CTkFrame(l, fg_color="transparent")
        t.pack(side="left")
        ctk.CTkLabel(t, text=pet, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=info, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(l, text=status, text_color=txt, fg_color=bg, corner_radius=8, width=100, font=("Arial", 11, "bold")).pack(side="right", padx=10)

    def criar_item_alerta(self, master, pet, msg):
        i = ctk.CTkFrame(master, fg_color="transparent")
        i.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(i, text=pet, font=("Arial", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(i, text=msg, font=("Arial", 11), text_color="#64748B", wraplength=200, justify="left").pack(anchor="w")

    def criar_card_paciente(self, master, nome, status, info, icon, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        img = ctk.CTkFrame(c, fg_color="#CBD5E1", height=150, corner_radius=15)
        img.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(img, text=icon, font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(c, text=nome, font=("Arial", 18, "bold")).pack(anchor="w", padx=15, pady=(5,0))
        ctk.CTkLabel(c, text=info, font=("Arial", 12), text_color="#64748B").pack(anchor="w", padx=15)
        ctk.CTkButton(c, text="Ver detalhes", fg_color="white", text_color="black", border_width=1, corner_radius=15, height=35).pack(fill="x", padx=30, pady=20)

    def criar_card_agendamento_detalhado(self, master, hora, tit, sub):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0", height=80)
        c.pack(side="left", fill="x", expand=True)
        c.pack_propagate(False)
        ctk.CTkLabel(c, text="🕒", font=("Arial", 18)).pack(side="left", padx=20)
        ctk.CTkLabel(c, text=hora, font=("Arial", 16, "bold")).pack(side="left")
        t = ctk.CTkFrame(c, fg_color="transparent")
        t.pack(side="left", padx=20)
        ctk.CTkLabel(t, text=tit, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=sub, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(c, text="📍", font=("Arial", 18)).pack(side="right", padx=25)

    def criar_card_fin_topo(self, master, tit, val, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0", height=120)
        c.grid(row=0, column=col, padx=10, sticky="ew")
        ctk.CTkLabel(c, text=tit, text_color="#64748B", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(c, text=val, font=("Arial", 24, "bold"), text_color="black").pack()

    def criar_item_transacao(self, master, tit, data, val):
        i = ctk.CTkFrame(master, fg_color="transparent")
        i.pack(fill="x", padx=20, pady=10)
        t = ctk.CTkFrame(i, fg_color="transparent")
        t.pack(side="left")
        ctk.CTkLabel(t, text=tit, font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=data, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(i, text=val, text_color="#22C55E", font=("Arial", 13, "bold")).pack(side="right")


    def tela_prontuario(self):
            # Frame principal do prontuário
            container = ctk.CTkFrame(self.content, fg_color="transparent")
            container.pack(fill="both", expand=True, padx=30, pady=20)

            # HEADER DA TELA
            header = ctk.CTkFrame(container, fg_color="transparent")
            header.pack(fill="x", pady=(0, 20))

            titulo_box = ctk.CTkFrame(header, fg_color="transparent")
            titulo_box.pack(side="left")
            ctk.CTkLabel(titulo_box, text="Prontuário eletrônico", font=("Arial", 24, "bold"), text_color="black").pack(anchor="w")
            
            # Seletor de Pet (Para simular a escolha)
            self.pet_var = ctk.StringVar(value="thor (bulldog)")
            self.seletor_pet = ctk.CTkOptionMenu(titulo_box, values=["thor (bulldog)", "paçoca (vira-lata)", "luna (siamês)"],
                                                variable=self.pet_var, fg_color="white", text_color="black", 
                                                button_color="#E2E8F0", button_hover_color="#CBD5E1")
            self.seletor_pet.pack(side="left", pady=5)
            ctk.CTkLabel(titulo_box, text="Consulta atual:", font=("Arial", 13), text_color="#64748B").pack(side="left", padx=5)

            # Botão Salvar
            ctk.CTkButton(header, text="Salvar prontuário", fg_color="#A855F7", hover_color="#9333EA", 
                        font=("Arial", 14, "bold"), width=180, height=40).pack(side="right")

            # CORPO DIVIDIDO (ESQUERDA: EDITOR | DIREITA: HISTÓRICO)
            corpo = ctk.CTkFrame(container, fg_color="transparent")
            corpo.pack(fill="both", expand=True)
            corpo.columnconfigure(0, weight=3) # Coluna do Editor
            corpo.columnconfigure(1, weight=1) # Coluna do Histórico

            # --- LADO ESQUERDO: EDITOR DE ANOTAÇÕES ---
            editor_frame = ctk.CTkFrame(corpo, fg_color="transparent")
            editor_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

            ctk.CTkLabel(editor_frame, text="Anotações", font=("Arial", 16, "bold"), text_color="black").pack(anchor="w", pady=(0, 10))
            
            # Campo de texto grande
            self.txt_prontuario = ctk.CTkTextbox(editor_frame, corner_radius=20, border_width=1, 
                                                border_color="#94A3B8", fg_color="#E5E7EB", 
                                                text_color="black", font=("Arial", 14))
            self.txt_prontuario.pack(fill="both", expand=True)
            self.txt_prontuario.insert("1.0", "Digite aqui as observações, sintomas, temperatura, peso e procedimento realizados durante a consulta...")

            # --- LADO DIREITO: LISTA DE TODOS OS PRONTUÁRIOS ---
            historico_frame = ctk.CTkFrame(corpo, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
            historico_frame.grid(row=0, column=1, sticky="nsew")

            ctk.CTkLabel(historico_frame, text="Histórico de Prontuários", font=("Arial", 14, "bold")).pack(pady=15)

            # Scroll para os prontuários anteriores
            scroll_hist = ctk.CTkScrollableFrame(historico_frame, fg_color="transparent")
            scroll_hist.pack(fill="both", expand=True, padx=10, pady=5)

            # Simulação de registros anteriores
            self.criar_item_historico(scroll_hist, "15 Jan 2026", "Vacinação")
            self.criar_item_historico(scroll_hist, "02 Dez 2025", "Check-up Geral")
            self.criar_item_historico(scroll_hist, "10 Out 2025", "Tratamento Otite")

    def criar_item_historico(self, master, data, motivo):
            item = ctk.CTkFrame(master, fg_color="#F1F5F9", corner_radius=10, height=60)
            item.pack(fill="x", pady=5)
            item.pack_propagate(False)
            
            ctk.CTkLabel(item, text=data, font=("Arial", 12, "bold"), text_color="#1E293B").pack(anchor="w", padx=15, pady=(5,0))
            ctk.CTkLabel(item, text=motivo, font=("Arial", 11), text_color="#64748B").pack(anchor="w", padx=15)
            
            # Ícone de ver detalhes pequeno
            ctk.CTkLabel(item, text="📄", font=("Arial", 16)).place(relx=0.9, rely=0.5, anchor="center")



    