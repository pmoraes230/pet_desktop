import customtkinter as ctk
from modulo_dashboard import ModuloDashboard
from modulo_pacientes import ModuloPacientes
from modulo_chat import ModuloChat
from modulo_prontuario import ModuloProntuario
from modulo_agenda import ModuloAgenda
from modulo_financeiro import ModuloFinanceiro
from modulo_configuracoes import ModuloConfiguracoes

class DashboardVeterinario(ctk.CTkFrame, ModuloDashboard, ModuloPacientes, ModuloChat, 
                           ModuloProntuario, ModuloAgenda, ModuloFinanceiro, ModuloConfiguracoes):
    def __init__(self, master):
        super().__init__(master)

        self.menu_perfil_aberto = False
        self.menu_dropdown = None
        self.notif_aberta = False
        self.notif_dropdown = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=70)
        self.grid_rowconfigure(1, weight=1)

        # --- TOPBAR ---
        self.topbar = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew") 
        ctk.CTkLabel(self.topbar, text="Bom dia, Usuário!", font=("Arial", 16, "bold"), text_color="black").pack(side="left", padx=30)
        self.right_info = ctk.CTkFrame(self.topbar, fg_color="transparent"); self.right_info.pack(side="right", padx=20)
        self.btn_notif = ctk.CTkButton(self.right_info, text="🔔", font=("Arial", 20), width=40, height=40, fg_color="transparent", text_color="black", command=self.toggle_notifications)
        self.btn_notif.pack(side="left", padx=15)
        self.avatar = ctk.CTkButton(self.right_info, text="U", font=("Arial", 14, "bold"), width=38, height=38, fg_color="#A855F7", corner_radius=19, command=self.toggle_menu)
        self.avatar.pack(side="left")
        ctk.CTkFrame(self, fg_color="#E2E8F0", height=2).grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color="#0c5c54", width=260, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew"); self.sidebar.grid_propagate(False)
        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent"); logo_f.pack(pady=20, padx=10, fill="x")
        ctk.CTkLabel(logo_f, text="🐾 Coração em patas", font=("Arial", 15, "bold"), text_color="black").pack(side="left", padx=5)

        # --- CONTEÚDO ---
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0); self.content.grid(row=1, column=1, sticky="nsew")

        self.criar_botao_sidebar("Dashboard", self.tela_dashboard)
        self.criar_botao_sidebar("Mensagens", self.tela_chat) 
        self.criar_botao_sidebar("Pacientes", self.tela_pacientes)
        self.criar_botao_sidebar("Prontuário", self.tela_prontuario)
        self.criar_botao_sidebar("Agenda", self.tela_agenda)
        self.criar_botao_sidebar("Financeiro", self.tela_financeiro)
        
        self.tela_dashboard()

    def toggle_notifications(self):
        if self.notif_aberta:
            self.notif_dropdown.destroy(); self.notif_aberta = False
        else:
            if self.menu_perfil_aberto: self.toggle_menu()
            self.notif_dropdown = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.notif_dropdown.place(relx=0.92, rely=0.08, anchor="ne")
            ctk.CTkLabel(self.notif_dropdown, text="Notificações", font=("Arial", 14, "bold")).pack(pady=10, padx=20)
            self.notif_aberta = True

    def toggle_menu(self):
        if self.menu_perfil_aberto:
            self.menu_dropdown.destroy(); self.menu_perfil_aberto = False
        else:
            if self.notif_aberta: self.toggle_notifications()
            self.menu_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.menu_dropdown.place(relx=0.98, rely=0.08, anchor="ne")
            self.criar_item_aba("👤 Editar Perfil", self.tela_configuracoes_perfil)
            self.criar_item_aba("⚙️ Configurações", self.tela_configuracoes_gerais)
            self.menu_perfil_aberto = True

    def criar_item_aba(self, texto, comando, cor_texto="black"):
        btn = ctk.CTkButton(self.menu_dropdown, text=texto, fg_color="transparent", text_color=cor_texto, width=150, 
                            command=lambda: [self.toggle_menu(), self.trocar_tela(comando) if comando else None])
        btn.pack(padx=5, pady=2)

    def criar_botao_sidebar(self, texto, comando):
        ctk.CTkButton(self.sidebar, text=texto, fg_color="#14B8A6", hover_color="#188C7F", height=45, 
                      command=lambda: self.trocar_tela(comando)).pack(fill="x", padx=20, pady=6)

    def trocar_tela(self, func, *args):
        for widget in self.content.winfo_children(): widget.destroy()
        func(*args)