import customtkinter as ctk
from datetime import datetime
import app.core.colors as colors

# Controllers
from app.controllers.auth_controller import AuthController
from app.controllers.vet_controller import VetController
from app.controllers.pet_controller import PetController   # ← adicionado

# Módulos (agora composição, não herança)
from .modulo_pacientes import ModuloPacientes
from .modulo_financeiro import ModuloFinanceiro
from .modulo_configuracoes import ModuloConfiguracoes
from .modulo_agenda import ModuloAgenda
from .modulo_prontuario import ModuloProntuario
from .modulo_chat import ModuloChat

from app.views.modal import Modal

class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master, current_user: dict = None, on_logout=None):
        super().__init__(master)

        # ── Dados do usuário autenticado ─────────────────────────────────────
        self.current_user = current_user or {}
        self.current_user_id = self.current_user.get('id')
        self.user_name = self.current_user.get('name') or "Usuário"
        self.on_logout = on_logout

        # ── Controllers ──────────────────────────────────────────────────────
        self.vet_controller = VetController(self.current_user_id) if self.current_user_id else None
        self.pet_controller = PetController()

        # Variáveis de controle de UI
        self.menu_perfil_aberto = False
        self.menu_dropdown = None
        self.notif_aberta = False
        self.notif_dropdown = None

        # ── Layout principal ─────────────────────────────────────────────────
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=70)
        self.grid_rowconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=colors.BRAND_DARK_TEAL_HOVER, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=20, padx=10, fill="x")
        ctk.CTkLabel(logo_f, text="🐾 Coração em patas", font=("Arial", 15, "bold"), text_color="white").pack(side="left", padx=5)

        # Botões da sidebar (ainda sem os módulos — vamos configurar depois)
        self.criar_botao_sidebar("Dashboard",   self.tela_dashboard)
        self.criar_botao_sidebar("Mensagens",   lambda: None)  # placeholder por enquanto
        self.criar_botao_sidebar("Pacientes",   lambda: None)
        self.criar_botao_sidebar("Prontuário",  lambda: None)
        self.criar_botao_sidebar("Agenda",      lambda: None)
        self.criar_botao_sidebar("Financeiro",  lambda: None)

        # Topbar
        self.topbar = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.topbar.grid(row=0, column=1, sticky="nsew")
        self.topbar.grid_propagate(False)

        self.greeting_label = ctk.CTkLabel(
            self.topbar,
            text=f"{self._get_greeting()}, {self.user_name}!",
            font=("Arial", 16, "bold"),
            text_color="black"
        )
        self.greeting_label.pack(side="left", padx=30)

        self.right_info = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.right_info.pack(side="right", padx=20)

        self.btn_notif = ctk.CTkButton(
            self.right_info, text="🔔", font=("Arial", 20), width=40, height=40,
            fg_color="transparent", text_color="black", hover_color="#F1F5F9",
            command=self.toggle_notifications
        )
        self.btn_notif.pack(side="left", padx=15)

        initial = self.user_name[0].upper() if self.user_name else "U"
        self.avatar = ctk.CTkButton(
            self.right_info, text=initial, font=("Arial", 14, "bold"), width=38, height=38,
            fg_color="#A855F7", text_color="white", corner_radius=19,
            hover_color="#9333EA", command=self.toggle_menu
        )
        self.avatar.pack(side="left")

        ctk.CTkFrame(self, fg_color="#E2E8F0", height=2).grid(row=0, column=1, sticky="sew")

        # ── Área de conteúdo (CRIAR ANTES DOS MÓDULOS!) ───────────────────────
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")

        # ── AGORA sim: instanciar os módulos ─────────────────────────────────
        self.mod_pacientes = ModuloPacientes(self.content, self.pet_controller)
        self.mod_financeiro = ModuloFinanceiro(self.content)   # ajuste se precisar de controller
        self.mod_config = ModuloConfiguracoes(self.content)
        self.mod_agenda = ModuloAgenda(self.content)
        self.mod_prontuario = ModuloProntuario(self.content)
        self.mod_chat = ModuloChat(self.content)

        # ── Agora sim: configurar os botões da sidebar com os métodos reais ──
        # (substitua os lambdas placeholder de cima)
        botoes = [
            ("Dashboard",   self.tela_dashboard),
            ("Mensagens",   self.mod_chat.tela_chat),
            ("Pacientes",   self.mod_pacientes.tela_pacientes),
            ("Prontuário",  self.mod_prontuario.tela_prontuario),
            ("Agenda",      self.mod_agenda.tela_agenda),
            ("Financeiro",  self.mod_financeiro.tela_financeiro),
        ]

        # Limpa os botões placeholder e recria com os comandos corretos
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()

        for texto, comando in botoes:
            self.criar_botao_sidebar(texto, comando)

        # Tela inicial
        self.tela_dashboard()

    def _get_greeting(self) -> str:
        hora = datetime.now().hour
        if hora < 12: return "Bom dia"
        if hora < 18: return "Boa tarde"
        return "Boa noite"

    def criar_botao_sidebar(self, texto, comando):
        ctk.CTkButton(
            self.sidebar,
            text=texto,
            fg_color=colors.BRAND_DARK_TEAL_HOVER,
            hover_color="#188C7F",
            text_color="white",
            font=("Arial", 16),
            height=45,
            command=lambda: self.trocar_tela(comando)
        ).pack(fill="x", padx=20, pady=6)

    def trocar_tela(self, func, *args):
        for widget in self.content.winfo_children():
            widget.destroy()
        func(*args)

    # ── Telas do dashboard ───────────────────────────────────────────────
    def tela_dashboard(self):
        self.trocar_tela(self._construir_dashboard)

    def _construir_dashboard(self):
        # seu código atual do dashboard aqui (scroll, cards, histórico, alertas...)
        # mantive exatamente igual ao que você tinha
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        self.criar_card_metrica(scroll, "1,240", "Total Pacientes", "🟦", "+12%", 0)
        self.criar_card_metrica(scroll, "8", "Consultas hoje", "🟩", None, 1)
        self.criar_card_metrica(scroll, "4.2K", "Faturamento mês", "🟨", None, 2)

        ctk.CTkLabel(scroll, text="Histórico Recente", font=("Arial", 18, "bold"), text_color="black").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(30, 15), padx=10
        )
        ctk.CTkLabel(scroll, text="Alertas de saúde", font=("Arial", 18, "bold"), text_color="black").grid(
            row=1, column=2, sticky="w", pady=(30, 15), padx=10
        )

        hist_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        hist_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10)
        self.criar_linha_agendamento(hist_card, "09:00 AM", "Paçoca", "Vacinação Anual", "Confirmado", "#DCFCE7", "#166534")
        self.criar_linha_agendamento(hist_card, "10:30 AM", "Luna", "Avaliação", "Aguardando", "#FEF9C3", "#854D0E")

        al_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        al_card.grid(row=2, column=2, sticky="nsew", padx=10)
        self.criar_item_alerta(al_card, "Bob (Golden)", "Queda brusca de peso registrada.")

    def criar_card_metrica(self, master, valor, titulo, icon, badge, col):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0") 
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text=icon, font=("Arial", 24)).pack(anchor="w", padx=25, pady=(20, 0))
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=25)
        ctk.CTkLabel(f, text=valor, font=("Arial", 28, "bold"), text_color="black").pack(side="left")
        if badge:
            ctk.CTkLabel(f, text=badge, text_color="#22C55E", font=("Arial", 12, "bold")).pack(side="right")
        ctk.CTkLabel(card, text=titulo, text_color="#64748B", font=("Arial", 13)).pack(anchor="w", padx=25, pady=(0, 20))

    def criar_linha_agendamento(self, master, hora, pet, info, status, bg, txt):
        l = ctk.CTkFrame(master, fg_color="transparent") 
        l.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(l, text=hora, font=("Arial", 12, "bold"), width=70).pack(side="left")
        t = ctk.CTkFrame(l, fg_color="transparent")
        t.pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkLabel(t, text=pet, font=("Arial", 14, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(t, text=info, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(l, text=status, text_color=txt, fg_color=bg, corner_radius=8, width=100, font=("Arial", 11, "bold")).pack(side="right")

    def criar_item_alerta(self, master, pet, msg):
        i = ctk.CTkFrame(master, fg_color="transparent")
        i.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(i, text=pet, font=("Arial", 12, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(i, text=msg, font=("Arial", 11), text_color="#64748B", wraplength=220, justify="left").pack(anchor="w")

    # --- MENUS (DROPDOWN) ---
    def toggle_notifications(self):
        if self.notif_aberta:
            self.notif_dropdown.destroy()
            self.notif_aberta = False
        else:
            if self.menu_perfil_aberto: self.toggle_menu()
            self.notif_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.notif_dropdown.place(relx=0.95, y=75, anchor="ne")
            ctk.CTkLabel(self.notif_dropdown, text="Notificações", font=("Arial", 14, "bold"), text_color="black").pack(pady=10, padx=20)
            self.notif_aberta = True

    def toggle_menu(self):
        if self.menu_perfil_aberto:
            self.menu_dropdown.destroy()
            self.menu_perfil_aberto = False
        else:
            if self.notif_aberta: self.toggle_notifications()
            self.menu_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
            self.menu_dropdown.place(relx=0.98, y=75, anchor="ne")
            self.criar_item_aba("👤 Editar Perfil", self.tela_configuracoes_perfil)
            self.criar_item_aba("⚙️ Configurações", self.tela_configuracoes_gerais)
            ctk.CTkFrame(self.menu_dropdown, fg_color="#E2E8F0", height=1).pack(fill="x", padx=10, pady=5)
            
            # Botão Sair (Chama função de logout)
            self.criar_item_aba("🚪 Sair", self.fazer_logout, cor_texto="#EF4444")
            
            self.menu_perfil_aberto = True
    
    def fazer_logout(self):
        """Faz logout do usuário"""
        # Criar controller vazio apenas para limpar
        controller = AuthController("", "")
        controller.logout()
        
        # Mostrar confirmação
        Modal(self, "Logout", "Você foi desconectado com sucesso!", type="success")
        
        # Retornar à tela de login após 1 segundo
        if self.on_logout:
            self.after(1000, self.on_logout)

    def criar_item_aba(self, texto, comando, cor_texto="black"):
        btn = ctk.CTkButton(
            self.menu_dropdown, text=texto, fg_color="transparent", text_color=cor_texto, 
            hover_color="#F1F5F9", anchor="w", font=("Arial", 13), height=35, width=150,
            command=lambda: [self.toggle_menu(), comando() if comando else None]
        )
        btn.pack(padx=5, pady=2)
        