import customtkinter as ctk

class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Variáveis de controle para os menus
        self.menu_perfil_aberto = False
        self.menu_dropdown = None
        self.notif_aberta = False
        self.notif_dropdown = None

        # --- CONFIGURAÇÃO DE COLUNAS/LINHAS ---
        self.grid_columnconfigure(0, weight=0) # Coluna da Sidebar (fixa)
        self.grid_columnconfigure(1, weight=1) # Coluna do Conteúdo (expande)

        self.grid_rowconfigure(0, weight=0, minsize=70) # Altura da Topbar
        self.grid_rowconfigure(1, weight=1)             # Altura da Sidebar e Conteúdo

        # --- TOPBAR ---
        self.topbar = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew") 
        self.topbar.grid_propagate(False)

        ctk.CTkLabel(self.topbar, text="Bom dia, Usuário!", font=("Arial", 16, "bold"), text_color="black").pack(side="left", padx=30)
        
        self.right_info = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.right_info.pack(side="right", padx=20)
        
        # NOTIFICAÇÕES
        self.btn_notif = ctk.CTkButton(
            self.right_info, text="🔔", font=("Arial", 20), width=40, height=40,
            fg_color="transparent", text_color="black", hover_color="#F1F5F9",
            command=self.toggle_notifications
        )
        self.btn_notif.pack(side="left", padx=15)
        
        # AVATAR
        self.avatar = ctk.CTkButton(
            self.right_info, text="U", font=("Arial", 14, "bold"), width=38, height=38, 
            fg_color="#A855F7", text_color="white", corner_radius=19,
            hover_color="#9333EA", command=self.toggle_menu
        )
        self.avatar.pack(side="left")

        self.linha_separadora = ctk.CTkFrame(self, fg_color="#E2E8F0", height=2)
        self.linha_separadora.grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color="#14B8A6", width=260, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew") 
        self.sidebar.grid_propagate(False)

        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=20, padx=10, fill="x")

        self.logo_circle = ctk.CTkFrame(self.logo_frame, width=44, height=44, corner_radius=22, fg_color="#8B5CF6")
        self.logo_circle.pack(side="left", padx=(10, 5))
        self.logo_circle.pack_propagate(False)
        self.emoji_label = ctk.CTkLabel(self.logo_circle, text="🐾", font=("Arial", 20), text_color="white")
        self.emoji_label.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_text = ctk.CTkLabel(self.logo_frame, text="Coração em patas", font=("Arial", 15, "bold"), text_color="black")
        self.logo_text.pack(side="left", padx=5)

        # --- ÁREA DE CONTEÚDO ---
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")

        self.criar_botao_sidebar("Dashboard", self.tela_dashboard)
        self.criar_botao_sidebar("Mensagens", self.tela_chat) 
        self.criar_botao_sidebar("Pacientes", self.tela_pacientes)
        self.criar_botao_sidebar("Prontuário", self.tela_prontuario)
        self.criar_botao_sidebar("Agenda", self.tela_agenda)
        self.criar_botao_sidebar("Financeiro", self.tela_financeiro)
        
        self.tela_dashboard()

    # --- LÓGICA DAS NOTIFICAÇÕES ---
    def toggle_notifications(self):
        if self.notif_aberta:
            self.notif_dropdown.destroy()
            self.notif_aberta = False
        else:
            if self.menu_perfil_aberto: self.toggle_menu()
            self.notif_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
            self.notif_dropdown.place(relx=0.92, rely=0.08, anchor="ne")
            ctk.CTkLabel(self.notif_dropdown, text="Notificações", font=("Arial", 14, "bold")).pack(pady=10, padx=20, anchor="w")
            self.criar_item_notificacao("🐶 Paçoca precisa de vacina amanhã")
            self.criar_item_notificacao("📅 Nova consulta agendada: Thor")
            self.notif_aberta = True

    def criar_item_notificacao(self, texto):
        f = ctk.CTkFrame(self.notif_dropdown, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f, text=texto, font=("Arial", 12), wraplength=250, justify="left").pack(padx=10, pady=5)
        ctk.CTkFrame(self.notif_dropdown, fg_color="#F1F5F9", height=1).pack(fill="x", padx=10)

    # --- LÓGICA DO DROPDOWN DO PERFIL ---
    def toggle_menu(self):
        if self.menu_perfil_aberto:
            self.menu_dropdown.destroy()
            self.menu_perfil_aberto = False
        else:
            if self.notif_aberta: self.toggle_notifications()
            self.menu_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.menu_dropdown.place(relx=0.98, rely=0.08, anchor="ne")
            self.criar_item_aba("👤 Editar Perfil", self.tela_configuracoes_perfil)
            self.criar_item_aba("⚙️ Configurações", self.tela_configuracoes_gerais)
            ctk.CTkFrame(self.menu_dropdown, fg_color="#E2E8F0", height=1).pack(fill="x", padx=10, pady=5)
            self.criar_item_aba("🚪 Sair", None, cor_texto="#EF4444")
            self.menu_perfil_aberto = True

    def criar_item_aba(self, texto, comando, cor_texto="black"):
        btn = ctk.CTkButton(
            self.menu_dropdown, text=texto, fg_color="transparent", text_color=cor_texto,
            hover_color="#F1F5F9", anchor="w", font=("Arial", 13), height=35, width=150, 
            command=lambda: [self.toggle_menu(), self.trocar_tela(comando) if comando else None]
        )
        btn.pack(padx=5, pady=2)

    # --- LÓGICA DE NAVEGAÇÃO ---
    def criar_botao_sidebar(self, texto, comando):
        ctk.CTkButton(self.sidebar, text=texto, fg_color="#14B8A6", hover_color="#188C7F", 
                      text_color="white", font=("Arial", 16), height=45, 
                      command=lambda: self.trocar_tela(comando)).pack(fill="x", padx=20, pady=6)

    def trocar_tela(self, func, *args):
        for widget in self.content.winfo_children():
            widget.destroy()
        func(*args)

    # --- TELA: CHAT ---
    def tela_chat(self):
        chat_container = ctk.CTkFrame(self.content, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        chat_container.columnconfigure(0, weight=1)
        chat_container.columnconfigure(1, weight=3)
        chat_container.rowconfigure(0, weight=1)

        contatos_frame = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        contatos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(contatos_frame, text="Conversas", font=("Arial", 20, "bold")).pack(anchor="w", padx=25, pady=20)
        scroll_contatos = ctk.CTkScrollableFrame(contatos_frame, fg_color="transparent")
        scroll_contatos.pack(fill="both", expand=True, padx=10)
        self.criar_item_contato(scroll_contatos, "Ana (Tutor)", "🐶", True)
        self.criar_item_contato(scroll_contatos, "Carlos (Tutor)", "🐱")

        janela_chat = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        janela_chat.grid(row=0, column=1, sticky="nsew")
        header = ctk.CTkFrame(janela_chat, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(header, text="Conversando com Ana", font=("Arial", 16, "bold")).pack(side="left")
        self.area_msg = ctk.CTkScrollableFrame(janela_chat, fg_color="#F8FAFC", corner_radius=0)
        self.area_msg.pack(fill="both", expand=True)
        self.criar_bolha_mensagem(self.area_msg, "Olá Dr., a Paçoca está bem?", "09:41", "tutor")
        self.criar_bolha_mensagem(self.area_msg, "Olá! Sim, ela está ótima.", "09:45", "vet")
        input_f = ctk.CTkFrame(janela_chat, fg_color="white", height=80)
        input_f.pack(fill="x", side="bottom", padx=20, pady=20)
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
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=5)
        bolha = ctk.CTkFrame(f, fg_color=cor, corner_radius=15, border_width=1 if tipo=="tutor" else 0, border_color="#E2E8F0")
        bolha.pack(side=side)
        ctk.CTkLabel(bolha, text=texto, text_color=txt_cor, wraplength=250, justify="left").pack(padx=15, pady=10)
        ctk.CTkLabel(f, text=hora, font=("Arial", 9), text_color="#94A3B8").pack(side=side, padx=5)

    # --- TELA 1: DASHBOARD ---
    def tela_dashboard(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        metrics = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 30))
        metrics.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        self.criar_card_metrica(metrics, "1,240", "Total Pacientes", "🟦", "+12%", 0)
        self.criar_card_metrica(metrics, "8", "Consultas hoje", "🟩", None, 1)
        self.criar_card_metrica(metrics, "4.2K", "Faturamento mês", "🟨", None, 2)
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=3) 
        main_grid.columnconfigure(1, weight=2) 
        left_container = ctk.CTkFrame(main_grid, fg_color="transparent")
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        ctk.CTkLabel(left_container, text="Histórico Recente", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 15))
        hist_card = ctk.CTkFrame(left_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        hist_card.pack(fill="both", expand=True, ipady=10)
        self.criar_linha_agendamento(hist_card, "09:00 AM", "Paçoca", "Vacinação Anual", "Confirmado", "#DCFCE7", "#166534")
        self.criar_linha_agendamento(hist_card, "10:30 AM", "Luna", "Avaliação", "Aguardando", "#FEF9C3", "#854D0E")
        right_container = ctk.CTkFrame(main_grid, fg_color="transparent")
        right_container.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right_container, text="Alertas de saúde", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 15))
        al_card = ctk.CTkFrame(right_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        al_card.pack(fill="both", expand=True, padx=2)
        self.criar_item_alerta(al_card, "Bob (Golden)", "Queda brusca de peso registrada.")

    # --- TELA 2: PACIENTES ---
    def tela_pacientes(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Novo Paciente", fg_color="#14B8A6", width=150, corner_radius=10).pack(side="right")
        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 30))
        ctk.CTkEntry(search_row, placeholder_text="🔍 Pesquise por tutor ou pet", height=45, corner_radius=22).pack(side="left", fill="x", expand=True, padx=(0, 15))
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)
        self.criar_card_paciente(grid, "Paçoca", "Saudável", "Vira-lata • 4 Anos", "🐶", 0)
        self.criar_card_paciente(grid, "Luna", "Saudável", "Siamês • 2 Anos", "🐱", 1)
        self.criar_card_paciente(grid, "Thor", "Saudável", "Bulldog • 3 Anos", "🐶", 2)

    # --- TELA: PERFIL DO PET (TRANSFORMADO DO HTML) ---
    def tela_perfil_pet(self, nome_pet, raca_pet, emoji):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=30)
        
        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0) # Card esquerda
        container.columnconfigure(1, weight=1) # Conteúdo direita

        # --- LADO ESQUERDO: CARD PERFIL ---
        card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, width=350, border_width=1, border_color="#F1F5F9")
        card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        
        img_placeholder = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", height=220, corner_radius=30)
        img_placeholder.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(img_placeholder, text=emoji, font=("Arial", 80)).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card_esq, text=nome_pet, font=("Arial", 32, "bold"), text_color="#1E293B").pack()
        ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Arial", 12, "bold"), text_color="#14B8A6").pack(pady=(0, 20))
        
        tutor_box = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", corner_radius=15)
        tutor_box.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(tutor_box, text="TUTOR RESPONSÁVEL", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(tutor_box, text="Ana Souza", font=("Arial", 14, "bold"), text_color="#1E293B").pack(anchor="w", padx=15, pady=(0, 10))

        # Peso e Sexo
        row_stats = ctk.CTkFrame(card_esq, fg_color="transparent")
        row_stats.pack(fill="x", padx=20, pady=20)
        p_box = ctk.CTkFrame(row_stats, fg_color="#F0FDFA", corner_radius=15, height=80); p_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(p_box, text="PESO", font=("Arial", 10, "bold"), text_color="#134E4A").pack(pady=(10, 0))
        ctk.CTkLabel(p_box, text="12 kg", font=("Arial", 18, "bold"), text_color="#134E4A").pack()
        
        s_box = ctk.CTkFrame(row_stats, fg_color="#EFF6FF", corner_radius=15, height=80); s_box.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(s_box, text="SEXO", font=("Arial", 10, "bold"), text_color="#1E3A8A").pack(pady=(10, 0))
        ctk.CTkLabel(s_box, text="Macho", font=("Arial", 18, "bold"), text_color="#1E3A8A").pack()

        # Card Próxima Consulta
        prox_c = ctk.CTkFrame(card_esq, fg_color="#14B8A6", corner_radius=30)
        prox_c.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(prox_c, text="Próxima consulta", font=("Arial", 14), text_color="white").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(prox_c, text="15 de Fev", font=("Arial", 28, "bold"), text_color="white").pack(anchor="w", padx=20)
        ctk.CTkLabel(prox_c, text="Vacinação", font=("Arial", 14), text_color="white").pack(anchor="w", padx=20, pady=(0, 15))

        # --- LADO DIREITO: ABAS ---
        self.right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=40, border_width=1, border_color="#F1F5F9")
        self.right_col.grid(row=0, column=1, sticky="nsew")
        
        # Seletor de Abas
        tab_header = ctk.CTkFrame(self.right_col, fg_color="#F1F5F9", corner_radius=25, height=50)
        tab_header.pack(pady=30, padx=30, anchor="w")
        self.btn_sobre = ctk.CTkButton(tab_header, text="SOBRE", width=120, corner_radius=25, fg_color="#14B8A6", text_color="white", command=lambda: self.mudar_aba_pet("sobre"))
        self.btn_sobre.pack(side="left", padx=2, pady=2)
        self.btn_saude = ctk.CTkButton(tab_header, text="SAÚDE", width=120, corner_radius=25, fg_color="transparent", text_color="#64748B", hover_color="#E2E8F0", command=lambda: self.mudar_aba_pet("saude"))
        self.btn_saude.pack(side="left", padx=2, pady=2)

        self.container_abas = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.container_abas.pack(fill="both", expand=True, padx=40)
        
        self.mudar_aba_pet("sobre")

    def mudar_aba_pet(self, aba):
        for w in self.container_abas.winfo_children(): w.destroy()
        if aba == "sobre":
            self.btn_sobre.configure(fg_color="#14B8A6", text_color="white")
            self.btn_saude.configure(fg_color="transparent", text_color="#64748B")
            
            ctk.CTkLabel(self.container_abas, text="📝 Observações Gerais", font=("Arial", 16, "bold")).pack(anchor="w")
            txt = ctk.CTkTextbox(self.container_abas, fg_color="#F8FAFC", corner_radius=20, height=150, border_width=1, border_color="#E2E8F0")
            txt.pack(fill="x", pady=15)
            txt.insert("1.0", "Pet dócil, porém agitado em consultas. Histórico de alergia a certos medicamentos...")

            ctk.CTkLabel(self.container_abas, text="Comportamento", font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 10))
            tags = ["Brincalhão", "Curioso", "Agitado"]
            f_tags = ctk.CTkFrame(self.container_abas, fg_color="transparent")
            f_tags.pack(fill="x")
            for t in tags:
                ctk.CTkLabel(f_tags, text=t, fg_color="#F0FDFA", text_color="#14B8A6", corner_radius=15, padx=15, pady=5, font=("Arial", 11, "bold")).pack(side="left", padx=5)

        else: # ABA SAÚDE
            self.btn_saude.configure(fg_color="#14B8A6", text_color="white")
            self.btn_sobre.configure(fg_color="transparent", text_color="#64748B")
            
            h = ctk.CTkFrame(self.container_abas, fg_color="transparent")
            h.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(h, text="Protocolo de Vacinação", font=("Arial", 18, "bold")).pack(side="left")
            ctk.CTkButton(h, text="+ Novo Registro", fg_color="#14B8A6", width=120, corner_radius=20).pack(side="right")

            vacinas = [("V10", "10/01/2026", "10/01/2027"), ("Raiva", "15/12/2025", "15/12/2026")]
            for n, d, p in vacinas:
                v_card = ctk.CTkFrame(self.container_abas, fg_color="white", corner_radius=25, border_width=1, border_color="#F1F5F9")
                v_card.pack(fill="x", pady=10)
                ctk.CTkLabel(v_card, text="💉", font=("Arial", 25)).pack(side="left", padx=20, pady=20)
                ctk.CTkLabel(v_card, text=f"{n}\nAplicada: {d}", font=("Arial", 13, "bold"), justify="left").pack(side="left")
                ctk.CTkLabel(v_card, text=f"Reforço\n{p}", font=("Arial", 13, "bold"), text_color="#14B8A6", justify="right").pack(side="right", padx=20)

    # --- TELA 3: AGENDA ---
    def tela_agenda(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Agendamentos", font=("Arial", 24, "bold")).pack(side="left")
        badge = ctk.CTkFrame(header, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="Fevereiro 2026", font=("Arial", 14, "bold")).pack(padx=20, pady=5)
        dias_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        dias_frame.pack(fill="x", pady=(0, 30))
        dias_frame.columnconfigure((0,1,2,3,4,5,6), weight=1)
        dias = [("seg", "10"), ("ter", "11"), ("qua", "12"), ("qui", "13"), ("sex", "14"), ("sáb", "15"), ("dom", "16")]
        for i, (nome, num) in enumerate(dias):
            d_card = ctk.CTkFrame(dias_frame, fg_color="transparent")
            d_card.grid(row=0, column=i, pady=20)
            ctk.CTkLabel(d_card, text=nome, font=("Arial", 13), text_color="#64748B").pack()
            ctk.CTkLabel(d_card, text=num, font=("Arial", 16, "bold")).pack()
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
        ctk.CTkLabel(scroll, text="Painel Financeiro", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 25))
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
        for _ in range(3): self.criar_item_transacao(trans, "Pagamento: Paçoca", "Hoje, 14:30", "+ R$ 150,00")

    # --- TELA: PRONTUÁRIO ---
    def tela_prontuario(self):
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=20)
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        titulo_box = ctk.CTkFrame(header, fg_color="transparent")
        titulo_box.pack(side="left")
        ctk.CTkLabel(titulo_box, text="Prontuário eletrônico", font=("Arial", 24, "bold")).pack(anchor="w")
        self.pet_var = ctk.StringVar(value="thor (bulldog)")
        ctk.CTkOptionMenu(titulo_box, values=["thor (bulldog)", "paçoca (vira-lata)", "luna (siamês)"], variable=self.pet_var, fg_color="white", text_color="black", button_color="#E2E8F0").pack(side="left", pady=5)
        ctk.CTkButton(header, text="Salvar prontuário", fg_color="#A855F7", font=("Arial", 14, "bold"), width=180, height=40).pack(side="right")
        corpo = ctk.CTkFrame(container, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=1)
        editor = ctk.CTkFrame(corpo, fg_color="transparent")
        editor.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        ctk.CTkLabel(editor, text="Anotações", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
        txt = ctk.CTkTextbox(editor, corner_radius=20, border_width=1, border_color="#94A3B8", fg_color="#E5E7EB", text_color="black")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", "Digite aqui as observações...")
        hist = ctk.CTkFrame(corpo, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        hist.grid(row=0, column=1, sticky="nsew")
        scroll_h = ctk.CTkScrollableFrame(hist, fg_color="transparent")
        scroll_h.pack(fill="both", expand=True, padx=10, pady=15)
        self.criar_item_historico(scroll_h, "15 Jan 2026", "Vacinação")
        self.criar_item_historico(scroll_h, "02 Dez 2025", "Check-up Geral")

        # --- TELA 5: EDITAR PERFIL ---
    def tela_configuracoes_perfil(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        ctk.CTkLabel(scroll, text="Editar Perfil Profissional", font=("Arial", 24, "bold"), text_color="#1E293B").pack(pady=(0, 30))
        foto_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        foto_card.pack(fill="x", pady=(0, 20))
        foto_cont = ctk.CTkFrame(foto_card, fg_color="transparent")
        foto_cont.pack(pady=30)
        av = ctk.CTkFrame(foto_cont, width=120, height=120, corner_radius=60, fg_color="#F1F5F9", border_width=4, border_color="#14B8A6")
        av.pack(); av.pack_propagate(False)
        ctk.CTkLabel(av, text="U", font=("Arial", 40, "bold"), text_color="#14B8A6").place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkButton(foto_cont, text="📷", width=35, height=35, corner_radius=17, fg_color="#14B8A6").place(relx=0.9, rely=0.9, anchor="center")
        dados = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        dados.pack(fill="x", pady=(0, 30))
        ctk.CTkLabel(dados, text="👤  Dados Pessoais", font=("Arial", 16, "bold")).pack(anchor="w", padx=30, pady=20)
        grid = ctk.CTkFrame(dados, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=(0, 20)); grid.columnconfigure((0, 1), weight=1)
        self.criar_campo_input(grid, "NOME COMPLETO", "Usuário Exemplo", 0, 0)
        self.criar_campo_input(grid, "E-MAIL", "usuario@email.com", 0, 1)
        self.criar_campo_input(grid, "CRMV", "12345-SP", 1, 0)
        self.criar_campo_input(grid, "ESTADO (UF)", "São Paulo", 1, 1)

    # --- TELA 6: CONFIGURAÇÕES GERAIS ---
    def tela_configuracoes_gerais(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        ctk.CTkLabel(scroll, text="Configurações da Conta", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))
        c_lang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_lang.pack(fill="x", pady=10)
        ctk.CTkLabel(c_lang, text="🌐 Idioma", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=20)
        ctk.CTkOptionMenu(c_lang, values=["Português", "English"], fg_color="#F8FAFC", text_color="black").pack(side="right", padx=20)
        c_not = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_not.pack(fill="x", pady=10)
        ctk.CTkLabel(c_not, text="🔔 Notificações", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=15)
        for t in ["E-mail", "Lembretes", "Dicas semanais"]:
            f = ctk.CTkFrame(c_not, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=t).pack(side="left")
            ctk.CTkSwitch(f, text="").pack(side="right")
        c_dang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#FCA5A5")
        c_dang.pack(fill="x", pady=20)
        ctk.CTkLabel(c_dang, text="⚠️ Desativar conta", font=("Arial", 14, "bold"), text_color="#EF4444").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(c_dang, text="Essa ação não pode ser desfeita.", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkButton(c_dang, text="Desativar", fg_color="#EF4444", command=self.mostrar_modal).pack(anchor="w", padx=20, pady=15)

    def mostrar_modal(self):
        self.m_bg = ctk.CTkFrame(self, fg_color="black")
        self.m_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.m_box = ctk.CTkFrame(self, width=300, height=200, corner_radius=20)
        self.m_box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.m_box, text="Tem certeza?", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkButton(self.m_box, text="Cancelar", command=lambda:[self.m_bg.destroy(), self.m_box.destroy()]).pack(pady=5)

    # --- MÉTODOS AUXILIARES ---
    def criar_card_metrica(self, master, valor, titulo, icon, badge, col):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0") 
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text=icon, font=("Arial", 24)).pack(anchor="w", padx=25, pady=(20, 0))
        f = ctk.CTkFrame(card, fg_color="transparent"); f.pack(fill="x", padx=25)
        ctk.CTkLabel(f, text=valor, font=("Arial", 28, "bold")).pack(side="left")
        if badge: ctk.CTkLabel(f, text=badge, text_color="#22C55E", font=("Arial", 12, "bold")).pack(side="right")
        ctk.CTkLabel(card, text=titulo, text_color="#64748B", font=("Arial", 13)).pack(anchor="w", padx=25, pady=(0, 20))

    def criar_linha_agendamento(self, master, hora, pet, info, status, bg, txt):
        l = ctk.CTkFrame(master, fg_color="transparent") 
        l.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(l, text=hora, font=("Arial", 12, "bold"), width=70).pack(side="left")
        ctk.CTkLabel(l, text="🐶", font=("Arial", 20), fg_color="#F1F5F9", width=45, height=45, corner_radius=22).pack(side="left", padx=10, pady=10)
        t = ctk.CTkFrame(l, fg_color="transparent"); t.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t, text=pet, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=info, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(l, text=status, text_color=txt, fg_color=bg, corner_radius=8, width=100, font=("Arial", 11, "bold")).pack(side="right", padx=10)

    def criar_item_alerta(self, master, pet, msg):
        i = ctk.CTkFrame(master, fg_color="transparent"); i.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(i, text=pet, font=("Arial", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(i, text=msg, font=("Arial", 11), text_color="#64748B", wraplength=220, justify="left").pack(anchor="w", pady=(0, 10))

    def criar_card_paciente(self, master, nome, status, info, icon, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        img = ctk.CTkFrame(c, fg_color="#CBD5E1", height=150, corner_radius=15); img.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(img, text=icon, font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(c, text=nome, font=("Arial", 18, "bold")).pack(anchor="w", padx=15, pady=(5,0))
        ctk.CTkLabel(c, text=info, font=("Arial", 12), text_color="#64748B").pack(anchor="w", padx=15)
        # BOTÃO DETALHES AGORA LIGADO À NOVA TELA
        ctk.CTkButton(c, text="Ver detalhes", fg_color="white", text_color="black", border_width=1, corner_radius=15, height=35,
                      command=lambda: self.trocar_tela(self.tela_perfil_pet, nome, info, icon)).pack(fill="x", padx=30, pady=20)

    def criar_card_agendamento_detalhado(self, master, hora, tit, sub):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0") 
        c.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(c, text="🕒", font=("Arial", 18)).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(c, text=hora, font=("Arial", 16, "bold")).pack(side="left")
        t = ctk.CTkFrame(c, fg_color="transparent"); t.pack(side="left", padx=20, fill="x", expand=True)
        ctk.CTkLabel(t, text=tit, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=sub, font=("Arial", 11), text_color="#64748B").pack(anchor="w")

    def criar_card_fin_topo(self, master, tit, val, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0") 
        c.grid(row=0, column=col, padx=10, sticky="ew")
        ctk.CTkLabel(c, text=tit, text_color="#64748B", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(c, text=val, font=("Arial", 24, "bold")).pack(pady=(0, 20))

    def criar_item_transacao(self, master, tit, data, val):
        i = ctk.CTkFrame(master, fg_color="transparent"); i.pack(fill="x", padx=20, pady=10)
        t = ctk.CTkFrame(i, fg_color="transparent"); t.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t, text=tit, font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=data, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(i, text=val, text_color="#22C55E", font=("Arial", 13, "bold")).pack(side="right")

    def criar_item_historico(self, master, data, motivo):
        item = ctk.CTkFrame(master, fg_color="#F1F5F9", corner_radius=10) 
        item.pack(fill="x", pady=5)
        ctk.CTkLabel(item, text=data, font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10,0))
        ctk.CTkLabel(item, text=motivo, font=("Arial", 11), text_color="#64748B").pack(anchor="w", padx=15, pady=(0, 10))

    def criar_campo_input(self, master, label_text, placeholder, row, col):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        ctk.CTkLabel(f, text=label_text, font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=5)
        e = ctk.CTkEntry(f, height=45, corner_radius=12, border_width=0, fg_color="#F8FAFC", text_color="#1E293B", font=("Arial", 13, "bold"))
        e.insert(0, placeholder); e.pack(fill="x", pady=5)

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Sistema Veterinário")
    app.geometry("1280x720")
    dash = DashboardVeterinario(app)
    dash.pack(fill="both", expand=True)
    app.mainloop()