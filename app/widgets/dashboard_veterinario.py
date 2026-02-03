import customtkinter as ctk
from .modulo_pacientes import ModuloPacientes
from .modulo_financeiro import ModuloFinanceiro
from .modulo_configuracoes import ModuloConfiguracoes
from .modulo_agenda import ModuloAgenda
from .modulo_prontuario import ModuloProntuario
from .modulo_chat import ModuloChat

# Importação das funções que criam as telas
from app.widgets.screens.dashboard_screen import create_dashboard_screen
from app.widgets.screens.chat_screen import create_chat_screen
from app.widgets.screens.pacientes_screen import create_pacientes_screen
from app.widgets.screens.prontuario_screen import create_prontuario_screen
from app.widgets.screens.agenda_screen import create_agenda_screen
from app.widgets.screens.financeiro_screen import create_financeiro_screen
from app.widgets.screens.perfil_pet_screen import create_perfil_pet_screen
from app.widgets.screens.config_perfil_screen import create_config_perfil_screen
from app.widgets.screens.config_gerais_screen import create_config_gerais_screen


class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Variáveis de controle
        self.menu_perfil_aberto = False
        self.menu_dropdown = None
        self.notif_aberta = False
        self.notif_dropdown = None

        # --- CONFIGURAÇÃO DE COLUNAS/LINHAS ---
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Conteúdo

        self.grid_rowconfigure(0, weight=0, minsize=70)  # Topbar
        self.grid_rowconfigure(1, weight=1)              # Sidebar + Conteúdo

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

        # Linha separadora abaixo da topbar
        ctk.CTkFrame(self, fg_color="#E2E8F0", height=2).grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color="#14B8A6", width=260, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=20, padx=10, fill="x")
        ctk.CTkLabel(logo_f, text="🐾 Coração em patas", font=("Arial", 15, "bold"), text_color="black").pack(side="left", padx=5)

        # --- ÁREA DE CONTEÚDO ---
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")

        # Mapeamento de telas
        self.telas = {
            "dashboard":    create_dashboard_screen,
            "chat":         create_chat_screen,
            "pacientes":    create_pacientes_screen,
            "prontuario":   create_prontuario_screen,
            "agenda":       create_agenda_screen,
            "financeiro":   create_financeiro_screen,
            "perfil_pet":   create_perfil_pet_screen,      # recebe argumentos extras
            "config_perfil": create_config_perfil_screen,
            "config_gerais": create_config_gerais_screen,
        }

        # Botões da sidebar
        self.criar_botao_sidebar("Dashboard",   lambda: self.trocar_tela("dashboard"))
        self.criar_botao_sidebar("Mensagens",   lambda: self.trocar_tela("chat"))
        self.criar_botao_sidebar("Pacientes",   lambda: self.trocar_tela("pacientes"))
        self.criar_botao_sidebar("Prontuário",  lambda: self.trocar_tela("prontuario"))
        self.criar_botao_sidebar("Agenda",      lambda: self.trocar_tela("agenda"))
        self.criar_botao_sidebar("Financeiro",  lambda: self.trocar_tela("financeiro"))

        # Inicia na dashboard
        self.tela_dashboard()  # ou self.trocar_tela("dashboard")

    # ────────────────────────────────────────────────
    #  Métodos de controle (mantidos aqui porque são compartilhados)
    # ────────────────────────────────────────────────

    def toggle_notifications(self):
        if self.notif_aberta:
            self.notif_dropdown.destroy()
            self.notif_aberta = False
        else:
            if self.menu_perfil_aberto:
                self.toggle_menu()
            self.notif_dropdown = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=0)
            self.notif_dropdown.place(relx=0.92, rely=0.08, anchor="ne")
            self.notif_dropdown.lift()
            ctk.CTkLabel(self.notif_dropdown, text="Notificações", font=("Arial", 14, "bold")).pack(pady=10, padx=20, anchor="w")
            self.criar_item_notificacao("🐶 Paçoca precisa de vacina amanhã")
            self.criar_item_notificacao("📅 Nova consulta agendada: Thor")
            self.notif_aberta = True

    def criar_item_notificacao(self, texto):
        f = ctk.CTkFrame(self.notif_dropdown, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f, text=texto, font=("Arial", 12), wraplength=250, justify="left").pack(padx=10, pady=5)
        ctk.CTkFrame(self.notif_dropdown, fg_color="#E2E8F0", height=1).pack(fill="x", padx=15, pady=2)

    def toggle_menu(self):
        if self.menu_perfil_aberto:
            self.menu_dropdown.destroy()
            self.menu_perfil_aberto = False
        else:
            if self.notif_aberta:
                self.toggle_notifications()
            self.menu_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.menu_dropdown.place(relx=0.98, rely=0.08, anchor="ne")
            
            # Itens do Menu (Usando as funções dos Mixins)
            self.criar_item_aba("👤 Editar Perfil", self.tela_configuracoes_perfil)
            self.criar_item_aba("⚙️ Configurações", self.tela_configuracoes_gerais)
            
            # Separador
            ctk.CTkFrame(self.menu_dropdown, fg_color="#E2E8F0", height=1).pack(fill="x", padx=10, pady=5)
            
            # Botão Sair (Chama None ou comando de logout)
            self.criar_item_aba("🚪 Sair", None, cor_texto="#EF4444")
            
            self.menu_perfil_aberto = True

    def criar_item_aba(self, texto, comando, cor_texto="black"):
        btn = ctk.CTkButton(
            self.menu_dropdown, text=texto, fg_color="transparent", text_color=cor_texto,
            hover_color="#F1F5F9", anchor="w", font=("Arial", 13), height=35, width=150,
            command=lambda: [self.toggle_menu(), self.trocar_tela(comando) if comando else None]
        )
        btn.pack(padx=5, pady=2)

    def criar_botao_sidebar(self, texto, comando):
        ctk.CTkButton(
            self.sidebar, text=texto, fg_color="#14B8A6", hover_color="#188C7F",
            text_color="white", font=("Arial", 16), height=45,
            command=comando
        ).pack(fill="x", padx=20, pady=6)

    def trocar_tela(self, tela_nome, *args):
        for widget in self.content.winfo_children():
            widget.destroy()
        if tela_nome == "perfil_pet":
            self.telas[tela_nome](self.content, *args)
        else:
            self.telas[tela_nome](self.content)

    # Métodos de navegação que chamam as telas com argumentos
    def tela_dashboard(self):
        self.trocar_tela("dashboard")

    def tela_chat(self):
        self.trocar_tela("chat")

    def tela_pacientes(self):
        self.trocar_tela("pacientes")

    def tela_prontuario(self):
        self.trocar_tela("prontuario")

    def tela_agenda(self):
        self.trocar_tela("agenda")

    def tela_financeiro(self):
        self.trocar_tela("financeiro")

    def tela_configuracoes_perfil(self):
        self.trocar_tela("config_perfil")

    def tela_configuracoes_gerais(self):
        self.trocar_tela("config_gerais")

    # Popup (mantido aqui porque é chamado de várias telas)
    def abrir_popup_novo_paciente(self):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(self.overlay, width=400, height=520, corner_radius=20, border_width=2, border_color="#14B8A6")
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(modal, text="🐾 Novo Paciente", font=("Arial", 22, "bold"), text_color="#14B8A6").pack(pady=20)

        form = ctk.CTkFrame(modal, fg_color="transparent")
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

        btn_container = ctk.CTkFrame(modal, fg_color="transparent")
        btn_container.pack(fill="x", pady=25, padx=30)

        ctk.CTkButton(
            btn_container, text="Confirmar", fg_color="#14B8A6", hover_color="#0D9488",
            width=160, height=40, font=("Arial", 14, "bold"),
            command=self.fechar_popup
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_container, text="Cancelar", fg_color="#94A3B8", hover_color="#64748B",
            width=160, height=40, font=("Arial", 14, "bold"),
            command=self.fechar_popup
        ).pack(side="right", padx=5)

    def fechar_popup(self):
        if hasattr(self, 'overlay'):
            self.overlay.destroy()

    # Helpers que podem ser movidos depois para components/
    def criar_card_metrica(self, master, valor, titulo, icon, badge, col):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text=icon, font=("Arial", 24)).pack(anchor="w", padx=25, pady=(20, 0))
        f = ctk.CTkFrame(card, fg_color="transparent"); f.pack(fill="x", padx=25)
        ctk.CTkLabel(f, text=valor, font=("Arial", 28, "bold")).pack(side="left")
        if badge:
            ctk.CTkLabel(f, text=badge, text_color="#22C55E", font=("Arial", 12, "bold")).pack(side="right")
        ctk.CTkLabel(card, text=titulo, text_color="#64748B", font=("Arial", 13)).pack(anchor="w", padx=25, pady=(0, 20))

    def criar_linha_agendamento(self, master, hora, paciente, servico, status, bg_color, text_color):
        """Cria uma linha de agendamento no histórico"""
        linha = ctk.CTkFrame(master, fg_color="transparent")
        linha.pack(fill="x", pady=8)
        
        ctk.CTkLabel(linha, text=hora, font=("Arial", 11, "bold"), width=70).pack(side="left", padx=10)
        ctk.CTkLabel(linha, text=paciente, font=("Arial", 11), width=100).pack(side="left", padx=10)
        ctk.CTkLabel(linha, text=servico, font=("Arial", 11), width=150).pack(side="left", padx=10)
        
        status_frame = ctk.CTkFrame(linha, fg_color=bg_color, corner_radius=6)
        status_frame.pack(side="left", padx=10)
        ctk.CTkLabel(status_frame, text=status, text_color=text_color, font=("Arial", 10, "bold")).pack(padx=12, pady=4)

    def criar_item_alerta(self, master, nome, descricao, nivel="médio"):
        """Cria um item de alerta usado na tela de dashboard."""
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", pady=6)

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(row, text=nome, font=("Arial", 12, "bold")).pack(side="left", anchor="w")
        ctk.CTkLabel(row, text=descricao, font=("Arial", 11), text_color="#374151", wraplength=420, justify="left").pack(fill="x", padx=(10,0))

        # marcador de nível (baixa/médio/alta)
        cores = {"baixa": "#FDE68A", "médio": "#FECACA", "alta": "#FCA5A5"}
        cor = cores.get(nivel, "#FECACA")
        marcador = ctk.CTkFrame(f, width=10, height=10, corner_radius=5, fg_color=cor)
        marcador.place(relx=0.98, rely=0.5, anchor="e")
        
    def criar_item_contato(self, master, nome, emoji="🐶", online=False):
        """Cria um item de contato para a lista de conversas."""
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=8, pady=6)

        avatar = ctk.CTkFrame(f, width=38, height=38, corner_radius=19, fg_color="#F3F4F6")
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=emoji, font=("Arial", 14)).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(f, fg_color="transparent")
        info.pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(info, text=nome, font=("Arial", 12, "bold")).pack(anchor="w")
        status_text = "Online" if online else "Offline"
        status_color = "#10B981" if online else "#9CA3AF"
        ctk.CTkLabel(info, text=status_text, text_color=status_color, font=("Arial", 11)).pack(anchor="w")
        
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

    # ... adicione aqui outros métodos auxiliares que forem usados em várias telas
    # (criar_linha_agendamento, criar_card_paciente, etc.)
