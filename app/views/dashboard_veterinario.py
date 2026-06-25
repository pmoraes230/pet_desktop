import customtkinter as ctk
from datetime import datetime
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading

# Controllers (assumindo que já existem e estão funcionando)
from app.controllers.auth_controller import AuthController
from app.controllers.vet_controller import VetController
from app.controllers.pet_controller import PetController
from app.controllers.perfil_controller import FotoPerfil
from app.controllers.prontuario_controller import ProntuarioController
from app.services.s3_client import get_url_s3
from app.core.i18n import get_language, set_language as set_app_language, tr
from app.core.theme import is_dark_mode, set_appearance_mode

# Módulos (assumindo que já existem)
from .modulo_pacientes import ModuloPacientes
from .modulo_financeiro import ModuloFinanceiro
from .modulo_configuracoes import ModuloConfiguracoes
from .modulo_agenda import ModuloAgenda
from .modulo_prontuario import ModuloProntuario
from .modulo_chat import ModuloChat

from app.views.modal import Modal

# Cores atualizadas para o novo tema (simulando cores.py, mas embutido para clareza)
class Colors:
    PRIMARY_DARK = "#2E7D7D"  # Um verde-azulado mais escuro para a sidebar
    PRIMARY = "#4CAF50" # Verde para ícones e destaque
    PRIMARY_HOVER = "#388E8E"
    NEUTRAL_50 = "#F8F9FA"  # Fundo principal muito claro
    NEUTRAL_100 = "#EAECEF" # Hover em botões claros
    NEUTRAL_200 = "#E0E3E8" # Bordas de cards
    NEUTRAL_300 = "#CCD1D9" # Separadores
    NEUTRAL_500 = "#6B7280" # Ícones e texto secundário
    TEXT_PRIMARY = "#343A40" # Texto principal escuro
    TEXT_SECONDARY = "#6C757D" # Texto secundário
    DANGER = "#DC3545" # Vermelho para ações perigosas/logout
    SUCCESS = "#28A745" # Verde para sucesso
    SUCCESS_BG = "#E6FFED" # Fundo suave para status de sucesso

    # Cores específicas para os novos cards de métricas
    METRIC_ICON_1 = "#8A2BE2" # Roxo para Total Pacientes
    METRIC_ICON_2 = "#FFC107" # Amarelo para Consultas Hoje
    METRIC_ICON_3 = "#DC3545" # Vermelho para Casos Críticos
    METRIC_ICON_4 = "#28A745" # Verde para Faturamento Mensal

    def apply_appearance(self):
        if is_dark_mode():
            self.PRIMARY_DARK = "#0F766E"
            self.PRIMARY = "#14B8A6"
            self.PRIMARY_HOVER = "#115E59"
            self.NEUTRAL_50 = "#111827"
            self.NEUTRAL_100 = "#1F2937"
            self.NEUTRAL_200 = "#374151"
            self.NEUTRAL_300 = "#4B5563"
            self.NEUTRAL_500 = "#9CA3AF"
            self.TEXT_PRIMARY = "#F9FAFB"
            self.TEXT_SECONDARY = "#D1D5DB"
            self.SUCCESS_BG = "#064E3B"
            return

        self.PRIMARY_DARK = "#2E7D7D"
        self.PRIMARY = "#4CAF50"
        self.PRIMARY_HOVER = "#388E8E"
        self.NEUTRAL_50 = "#F8F9FA"
        self.NEUTRAL_100 = "#EAECEF"
        self.NEUTRAL_200 = "#E0E3E8"
        self.NEUTRAL_300 = "#CCD1D9"
        self.NEUTRAL_500 = "#6B7280"
        self.TEXT_PRIMARY = "#343A40"
        self.TEXT_SECONDARY = "#6C757D"
        self.SUCCESS_BG = "#E6FFED"
    
colors = Colors() # Instância para uso
colors.apply_appearance()

class DashboardVeterinario(ctk.CTkFrame):
    """
    Dashboard principal do veterinário - design moderno e profissional (2025)
    Mantém todas as funcionalidades originais com visual atualizado
    """

    def __init__(self, master, current_user: dict = None, on_logout=None):
        super().__init__(master)

        self.current_user = current_user or {}
        self.user_id = self.current_user.get('id')
        self.user_name = self.current_user.get('name') or "Usuário"
        self.on_logout = on_logout

        # Controllers (garantindo que não seja None se user_id for None)
        self.vet_ctrl = VetController(self.user_id) if self.user_id else None
        self.pet_ctrl = PetController(self.user_id)
        self.prontuario_ctrl = ProntuarioController(self.user_id) if self.user_id else None
        self.foto_perfil_ctrl = FotoPerfil(self.user_id)

        # Estados UI
        self.profile_menu_open = False
        self.profile_menu = None
        self.notifications_open = False
        self.notifications_menu = None
        self.avatar_image = None
        self.language = get_language()
        self.current_screen_title_key = "dashboard"
        self.sidebar_buttons = []

        # Fundo geral mais limpo e moderno
        self.configure(fg_color=colors.NEUTRAL_50)

        self._setup_layout()

        # Ordem correta: content primeiro → módulos → sidebar/topbar
        self._build_content_frame()
        self._init_modules()
        self._build_sidebar()
        self._build_topbar()

        # Carrega avatar em thread separada
        threading.Thread(target=self._load_avatar_background, daemon=True).start()

        # Tela inicial
        self.show_dashboard()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=70)   # um pouco mais alto
        self.grid_rowconfigure(1, weight=1)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=colors.PRIMARY_DARK,  # teal escuro sofisticado
            width=260, # Largura ajustada
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo + nome do sistema e do Dr.
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(pady=(30, 20), padx=28, fill="x")

        # Mantém o logo existente
        logo_path = "app/assets/pet.png" # Verifique se o caminho da imagem está correto
        try:
            logo = ctk.CTkImage(Image.open(logo_path), size=(32, 32)) # Tamanho ajustado
            ctk.CTkLabel(header, image=logo, text="").pack(side="left", padx=(0, 12))
        except FileNotFoundError:
            print(f"Erro: Imagem do logo não encontrada em {logo_path}. Usando placeholder.")
            ctk.CTkLabel(header, text="🐾", font=("Segoe UI", 32), text_color="white").pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            header,
            text=tr("Coração em Patas"),
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="white",
        ).pack(side="left")
        
        # Nome do Dr. e CRMV
        ctk.CTkLabel(
            self.sidebar,
            text=f"Dr. {self.user_name} - CRMV 3321", # CRMV fixo para exemplo
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=colors.NEUTRAL_200, # Cor mais clara para info secundária
        ).pack(fill="x", padx=28, pady=(0, 30))


        # Navegação moderna
        nav_items = [
            ("dashboard", self.show_dashboard, "🏠"),
            ("messages", lambda: self.mod_chat.tela_chat(), "💬"),
            ("patients", lambda: self.mod_pacientes.tela_pacientes(), "🐾"),
            ("schedule", lambda: self.mod_agenda.tela_agenda(), "📅"),
            ("records", lambda: self.mod_prontuario.tela_prontuario(), "📋"), # Ordem ajustada
            ("finance", lambda: self.mod_financeiro.tela_financeiro(), "💰"),
        ]

        for key, command, icon_str in nav_items:
            self._create_sidebar_button(key, command, icon_str)

    def _create_sidebar_button(self, key: str, command, icon_str: str):
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"{icon_str}   {self._t(key)}", # Usa o ícone string diretamente
            fg_color="transparent",
            hover_color=colors.PRIMARY_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=48, # Altura ajustada
            corner_radius=10, # Raio menor
            anchor="w",
            command=lambda: self._switch_screen(command, key),
        )
        btn.pack(fill="x", padx=20, pady=4) # Padding ajustado
        self.sidebar_buttons.append((btn, key, icon_str))

    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self, fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white", corner_radius=0)
        self.topbar.grid(row=0, column=1, sticky="ew")
        self.topbar.configure(border_width=0) # Garante sem borda

        # Título "Dashboard" ou da tela atual
        self.current_screen_title = ctk.CTkLabel(
            self.topbar,
            text=self._t("dashboard"), # Valor inicial
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        )
        self.current_screen_title.pack(side="left", padx=40, pady=16)

        # Área direita com espaçamento maior
        right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right.pack(side="right", padx=32)

        # Notificações (apenas ícone)
        btn_notif = ctk.CTkButton(
            right,
            text="🔔",
            font=("Segoe UI Emoji", 20),
            fg_color="transparent",
            hover_color=colors.NEUTRAL_100,
            text_color=colors.NEUTRAL_500,
            width=40, height=40, corner_radius=20,
            command=self._toggle_notifications,
        )
        btn_notif.pack(side="left", padx=(0, 16))

        # Try to load avatar synchronously from already-initialized ModuloConfiguracoes
        initial_avatar = None
        try:
            perfil = None
            if hasattr(self, 'mod_configuracoes') and getattr(self.mod_configuracoes, 'perfil_data', None):
                perfil = self.mod_configuracoes.perfil_data
            elif self.foto_perfil_ctrl:
                perfil = self.foto_perfil_ctrl.fetch_perfil_data()

            key = perfil.get('imagem_perfil_veterinario') if perfil else None
            if key:
                url = get_url_s3(key, expires_in=604800)
                if url:
                    resp = requests.get(url, timeout=4)
                    resp.raise_for_status()
                    img_pil = Image.open(BytesIO(resp.content))
                    img_round = self._create_circular_image(img_pil, (40, 40))
                    initial_avatar = ctk.CTkImage(light_image=img_round, size=(40, 40))
                    self.avatar_image = initial_avatar
        except Exception:
            initial_avatar = None

        self.profile_button_text = self._profile_button_text()
        self.avatar_btn = ctk.CTkButton(
            right,
            text=self.profile_button_text,
            image=initial_avatar,
            compound="left",
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            hover_color=colors.NEUTRAL_100,
            text_color=colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            width=240,
            height=60,
            corner_radius=20,
            anchor="w",
            command=self._toggle_profile_menu,
        )
        self.avatar_btn.pack(side="left", padx=(0, 8), pady=4)
        self.avatar_image = None


    def _build_content_frame(self):
        self.content = ctk.CTkFrame(self, fg_color=colors.NEUTRAL_50)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _init_modules(self):
        # Passa 'self' para o módulo de configurações para que ele possa chamar atualizar_avatar
        self.mod_pacientes = ModuloPacientes(self.content, self.pet_ctrl)
        self.mod_financeiro = ModuloFinanceiro(self.content)
        self.mod_configuracoes = ModuloConfiguracoes(self.content, parent=self, on_avatar_updated=self.atualizar_avatar)
        self.mod_agenda = ModuloAgenda(self.content, self.user_id)
        self.mod_prontuario = ModuloProntuario(self.content, self.prontuario_ctrl)
        self.mod_chat = ModuloChat(self.content)

    def _switch_screen(self, target_screen_func, title="Dashboard"):
        for child in self.content.winfo_children():
            child.destroy()
        target_screen_func()
        self.current_screen_title_key = self._title_to_key(title)
        self.current_screen_title.configure(text=self._t(self.current_screen_title_key)) # Atualiza o título da topbar

    def set_language(self, language: str):
        self.language = "en" if language == "en" else "pt"
        set_app_language(self.language)
        self._refresh_language_texts()

    def set_theme_mode(self, mode: str):
        set_appearance_mode(mode)
        colors.apply_appearance()
        self._refresh_theme_colors()

    def _refresh_theme_colors(self):
        self.configure(fg_color=colors.NEUTRAL_50)
        if hasattr(self, "content"):
            self.content.configure(fg_color=colors.NEUTRAL_50)
        if hasattr(self, "sidebar"):
            self.sidebar.configure(fg_color=colors.PRIMARY_DARK)
        if hasattr(self, "topbar"):
            self.topbar.configure(fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white")
        if hasattr(self, "current_screen_title"):
            self.current_screen_title.configure(text_color=colors.TEXT_PRIMARY)
        if hasattr(self, "avatar_btn"):
            self.avatar_btn.configure(
                fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
                hover_color=colors.NEUTRAL_200 if is_dark_mode() else colors.NEUTRAL_100,
                text_color=colors.TEXT_PRIMARY,
            )
        for btn, _key, _icon_str in self.sidebar_buttons:
            btn.configure(hover_color=colors.PRIMARY_HOVER)
        if self.profile_menu_open:
            self._toggle_profile_menu()
        if self.notifications_open:
            self._toggle_notifications()

    def _refresh_language_texts(self):
        for btn, key, icon_str in self.sidebar_buttons:
            btn.configure(text=f"{icon_str}   {self._t(key)}")
        self.profile_button_text = self._profile_button_text()
        if hasattr(self, "avatar_btn"):
            self.avatar_btn.configure(text=self.profile_button_text)
        if hasattr(self, "current_screen_title"):
            self.current_screen_title.configure(text=self._t(self.current_screen_title_key))
        try:
            self.winfo_toplevel().title(tr("Coração em Patas"))
        except Exception:
            pass
        if self.profile_menu_open:
            self._toggle_profile_menu()
            self._toggle_profile_menu()

    def _profile_button_text(self):
        return f"{self.user_name}\n{self._t('my_profile')}  ⌄"

    def _title_to_key(self, title):
        title_map = {
            "Dashboard": "dashboard",
            "Mensagens": "messages",
            "Pacientes": "patients",
            "Agenda": "schedule",
            "Prontuários": "records",
            "Prontuario": "records",
            "Financeiro": "finance",
            "Meu Perfil": "my_profile",
            "Configurações": "settings",
            "Configuracoes": "settings",
        }
        return title_map.get(title, title if title in self._translations().get("pt", {}) else "dashboard")

    def _translations(self):
        return {
            "pt": {
                "dashboard": "Dashboard",
                "messages": "Mensagens",
                "patients": "Pacientes",
                "schedule": "Agenda",
                "records": "Prontuários",
                "finance": "Financeiro",
                "my_profile": "Meu Perfil",
                "settings": "Configurações",
                "logout": "Sair da conta",
                "notifications": "Notificações",
                "no_notifications": "Nenhuma notificação no momento",
                "notification": "Notificação",
                "new_appointment": "Novo Agendamento",
                "sample_notification": "Dr. Rayan, você tem um novo agendamento para amanhã.",
                "today_schedule": "Agenda de Hoje",
                "no_today_appointments": "Nenhuma consulta agendada para hoje.",
                "view_all": "Ver tudo",
                "alerts": "Alertas",
                "no_alerts": "Nenhum alerta pendente.",
                "total_patients": "Total Pacientes",
                "today_appointments": "Consultas Hoje",
                "critical_cases": "Casos Críticos",
                "today_revenue": "Faturamento Hoje",
            },
            "en": {
                "dashboard": "Dashboard",
                "messages": "Messages",
                "patients": "Patients",
                "schedule": "Schedule",
                "records": "Medical Records",
                "finance": "Finance",
                "my_profile": "My Profile",
                "settings": "Settings",
                "logout": "Sign out",
                "notifications": "Notifications",
                "no_notifications": "No notifications right now",
                "notification": "Notification",
                "new_appointment": "New Appointment",
                "sample_notification": "Dr. Rayan, you have a new appointment for tomorrow.",
                "today_schedule": "Today's Schedule",
                "no_today_appointments": "No appointments scheduled for today.",
                "view_all": "View all",
                "alerts": "Alerts",
                "no_alerts": "No pending alerts.",
                "total_patients": "Total Patients",
                "today_appointments": "Today's Appointments",
                "critical_cases": "Critical Cases",
                "today_revenue": "Today's Revenue",
            },
        }

    def _t(self, key):
        return self._translations().get(self.language, {}).get(key, tr(key))

    # ── Telas ────────────────────────────────────────────────────────────────

    def show_dashboard(self):
        self._switch_screen(self._build_dashboard_screen, "dashboard")

    def _build_dashboard_screen(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=30) # Padding ajustado

        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="group1") # 4 colunas para as métricas

        metrics = self.vet_ctrl.fetch_metrics() if self.vet_ctrl else {}
        # Valores simulados para teste se vet_ctrl for None
        if not self.vet_ctrl:
            metrics = {
                "total_pets": 4,
                "consultas_hoje": 0,
                "casos_criticos": 0,
                "faturamento_mes": 0.00
            }


        # Novos cards de métricas (4 ao invés de 3)
        self._create_metric_card(
            scroll, metrics.get("total_pets", 0), self._t("total_patients"), "👥", 0,
            icon_color=colors.METRIC_ICON_1
        )
        self._create_metric_card(
            scroll, metrics.get("consultas_hoje", 0), self._t("today_appointments"), "🗓️", 1,
            icon_color=colors.METRIC_ICON_2
        )
        self._create_metric_card(
            scroll, metrics.get("casos_criticos", 0), self._t("critical_cases"), "⚠️", 2, # Novo card
            icon_color=colors.METRIC_ICON_3
        )
        self._create_metric_card(
            scroll,
            metrics.get("faturamento_mes", 0),
            self._t("today_revenue"), # Texto ajustado
            "💲", # Ícone ajustado
            3,
            prefix="R$ ",
            icon_color=colors.METRIC_ICON_4
        )
        
        # Agenda de Hoje
        agenda_frame = ctk.CTkFrame(
            scroll,
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            corner_radius=16, # Menor raio
            border_width=1,
            border_color=colors.NEUTRAL_200,
        )
        agenda_frame.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=(30, 0), sticky="nsew") # Ajustado para 2 colunas

        ctk.CTkLabel(
            agenda_frame,
            text=self._t("today_schedule"),
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(padx=24, pady=(20, 10), anchor="w")

        # Conteúdo da agenda (simulado)
        agenda_content = ctk.CTkFrame(agenda_frame, fg_color="transparent")
        agenda_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Simulação de consultas vazias
        ctk.CTkLabel(
            agenda_content,
            text="☕", # Ícone de café para "nenhuma consulta"
            font=("Segoe UI", 48),
            text_color=colors.NEUTRAL_300,
        ).pack(pady=(20, 10))
        ctk.CTkLabel(
            agenda_content,
            text=self._t("no_today_appointments"),
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY,
        ).pack(pady=(0, 40))

        # Botão "Ver tudo"
        ctk.CTkButton(
            agenda_frame,
            text=self._t("view_all"),
            fg_color="transparent",
            hover_color=colors.NEUTRAL_100,
            text_color=colors.PRIMARY_DARK, # Cor do texto do botão
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=lambda: self._switch_screen(self.mod_agenda.tela_agenda, "schedule"),
        ).place(relx=0.95, rely=0.08, anchor="e") # Posicionamento para ficar no canto superior direito

        # Alertas (novo card)
        alerts_frame = ctk.CTkFrame(
            scroll,
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            corner_radius=16,
            border_width=1,
            border_color=colors.NEUTRAL_200,
        )
        alerts_frame.grid(row=1, column=2, columnspan=2, padx=(20, 0), pady=(30, 0), sticky="nsew")

        ctk.CTkLabel(
            alerts_frame,
            text=self._t("alerts"),
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(padx=24, pady=(20, 10), anchor="w")

        # Conteúdo dos alertas (simulado)
        alerts_content = ctk.CTkFrame(alerts_frame, fg_color="transparent")
        alerts_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            alerts_content,
            text=self._t("no_alerts"),
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY,
        ).pack(pady=60)


    def _create_metric_card(self, parent, value, title, icon_str, col, prefix="", icon_color=None):
        card = ctk.CTkFrame(
            parent,
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            corner_radius=16, # Raio ajustado
            border_width=1,
            border_color=colors.NEUTRAL_200,
        )
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew") # Padding ajustado

        icon_frame = ctk.CTkFrame(
            card,
            fg_color=colors.NEUTRAL_200 if is_dark_mode() else colors.NEUTRAL_100,
            width=48,
            height=48,
            corner_radius=12,
        )
        icon_frame.pack_propagate(False) # Impede que o frame se encolha
        icon_frame.pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            icon_frame,
            text=icon_str, # Usa o ícone string
            font=("Segoe UI Emoji", 22),
            width=48,
            height=48,
            text_color=icon_color or colors.PRIMARY, # Cor do ícone
        ).pack(expand=True) # Centraliza o ícone no frame

        display_value = f"{prefix}{value:,.2f}".replace('.', ',') if isinstance(value, (int, float)) else str(value)
        ctk.CTkLabel(
            card,
            text=display_value,
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"), # Tamanho ajustado
            text_color=colors.TEXT_PRIMARY,
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Helvetica", size=13), # Tamanho da fonte ajustado
            text_color=colors.TEXT_SECONDARY,
        ).pack(anchor="w", padx=20, pady=(4, 20))

    # _build_recent_pets_list e _create_pet_history_row foram removidos pois a seção "Atendimentos Recentes" foi substituída.
    # Se precisar de uma lista de "últimos pacientes", ela precisaria ser redesenhada para se ajustar ao novo layout.

    # ── Avatar ───────────────────────────────────────────────────────────────

    def _load_avatar_background(self):
        try:
            perfil = self.foto_perfil_ctrl.fetch_perfil_data()
            key = perfil.get("imagem_perfil_veterinario")
            if not key:
                # Carrega um avatar padrão se não houver imagem
                self.after(0, lambda: self.avatar_btn.configure(text="👤", image=None))
                return

            url = get_url_s3(key, expires_in=604800)
            if not url:
                self.after(0, lambda: self.avatar_btn.configure(text="👤", image=None))
                return

            session = requests.Session()
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
            session.mount("https://", HTTPAdapter(max_retries=retries))

            resp = session.get(url, timeout=10)
            resp.raise_for_status()

            img_pil = Image.open(BytesIO(resp.content))
            img_round = self._create_circular_image(img_pil, (40, 40)) # Tamanho do avatar ajustado
            ctk_img = ctk.CTkImage(light_image=img_round, size=(40, 40))

            self.avatar_image = ctk_img
            self.after(0, lambda img=ctk_img: self.avatar_btn.configure(image=img, text=self.profile_button_text))

        except Exception as e:
            print(f"Falha ao carregar avatar: {e}")
            self.avatar_image = None
            self.after(0, lambda: self.avatar_btn.configure(text=self.profile_button_text, image=None)) # Garante que o texto apareça em caso de falha

    def _create_circular_image(self, img: Image.Image, size: tuple) -> Image.Image:
        img = img.resize(size, Image.LANCZOS).convert("RGBA")
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = Image.new("RGBA", size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)
        return output

    # ── Menus ────────────────────────────────────────────────────────────────

    def _toggle_notifications(self):
        # Lógica de notificação pode ser simplificada ou ajustada para o novo design
        # A segunda imagem não mostra um menu de notificações, então manterei o básico
        if self.notifications_open:
            if self.notifications_menu and self.notifications_menu.winfo_exists():
                self.notifications_menu.destroy()
            self.notifications_open = False
            return

        if self.profile_menu_open:
            self._toggle_profile_menu()

        self.notifications_menu = ctk.CTkFrame(
            self,
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            corner_radius=12, # Raio ajustado
            border_width=1,
            border_color=colors.NEUTRAL_200,
            width=300 # Largura ajustada
        )
        # Posiciona o menu de notificações mais próximo do ícone
        self.notifications_menu.place(relx=0.96, y=60, anchor="ne") 

        ctk.CTkLabel(
            self.notifications_menu,
            text=self._t("notifications"),
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(pady=12, padx=16, anchor="w")

        scroll = ctk.CTkScrollableFrame(self.notifications_menu, fg_color="transparent", height=200) # Altura ajustada
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        notifications = self.vet_ctrl.fetch_alerts() if self.vet_ctrl else []
        # Simula alerts
        if not notifications and not self.vet_ctrl:
            notifications = [{"id": 1, "tipo": self._t("new_appointment"), "mensagem": self._t("sample_notification"), "lida": False}]

        if not notifications:
            ctk.CTkLabel(
                scroll,
                text=self._t("no_notifications"),
                font=ctk.CTkFont(family="Helvetica", size=13),
                text_color=colors.TEXT_SECONDARY,
            ).pack(pady=40)
        else:
            for notif in notifications:
                self._create_notification_item(
                    scroll,
                    notif.get("tipo", self._t("notification")),
                    notif.get("mensagem", ""),
                    notif.get("id"),
                    bool(notif.get("lida", False)),
                )

        self.notifications_open = True

    def _create_notification_item(self, parent, title, message, notif_id=None, read=False):
        item = ctk.CTkFrame(parent, fg_color=colors.NEUTRAL_50 if not read else "transparent", corner_radius=8) # Fundo para não lidas
        item.pack(fill="x", padx=8, pady=4)

        title_lbl = ctk.CTkLabel(
            item,
            text=title,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=colors.TEXT_PRIMARY if not read else colors.TEXT_SECONDARY,
        )
        title_lbl.pack(anchor="w", padx=10, pady=(8, 0))

        msg_lbl = ctk.CTkLabel(
            item,
            text=message,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=colors.TEXT_SECONDARY,
            wraplength=250,
            justify="left",
        )
        msg_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        def mark_as_read(event=None):
            if notif_id and self.vet_ctrl:
                try:
                    self.vet_ctrl.mark_notification_read(notif_id)
                    title_lbl.configure(text_color=colors.TEXT_SECONDARY)
                    msg_lbl.configure(text_color=colors.TEXT_SECONDARY)
                    item.configure(fg_color="transparent") # Remove fundo de não lida
                    # Atualiza o badge de notificação (se houver)
                except Exception as e:
                    print(f"Erro ao marcar notificação como lida: {e}")

        item.bind("<Button-1>", mark_as_read)
        title_lbl.bind("<Button-1>", mark_as_read)
        msg_lbl.bind("<Button-1>", mark_as_read)


    def _toggle_profile_menu(self):
        if self.profile_menu_open:
            if self.profile_menu and self.profile_menu.winfo_exists():
                self.profile_menu.destroy()
            self.profile_menu_open = False
            return

        if self.notifications_open:
            self._toggle_notifications()

        self.profile_menu = ctk.CTkFrame(
            self,
            fg_color=colors.NEUTRAL_100 if is_dark_mode() else "white",
            corner_radius=20,
            border_width=1,
            border_color=colors.NEUTRAL_200,
            width=260,
        )
        self.profile_menu.place(relx=0.98, y=60, anchor="ne")

        header_frame = ctk.CTkFrame(self.profile_menu, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 12))

        avatar_frame = ctk.CTkFrame(
            header_frame,
            fg_color=colors.NEUTRAL_200 if is_dark_mode() else colors.NEUTRAL_100,
            width=54,
            height=54,
            corner_radius=27,
        )
        avatar_frame.pack(side="left", padx=(0, 12))
        avatar_frame.pack_propagate(False)

        ctk.CTkLabel(
            avatar_frame,
            image=self.avatar_image if self.avatar_image else None,
            text="" if self.avatar_image else "👤",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=24),
            text_color=colors.PRIMARY,
        ).pack(expand=True)

        user_name = self.current_user.get("name", "Usuário")
        user_email = self.current_user.get("email", "")

        text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            text_frame,
            text=user_name,
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            text_frame,
            text=user_email,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=colors.TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(self.profile_menu, text="", fg_color=colors.NEUTRAL_200, height=1).pack(fill="x", padx=16, pady=(8, 8))

        items = [
            (f"👤  {self._t('my_profile')}", lambda: self._switch_screen(self.mod_configuracoes.tela_configuracoes_perfil, "my_profile"), colors.TEXT_PRIMARY),
            (f"⚙️  {self._t('settings')}", lambda: self._switch_screen(self.mod_configuracoes.tela_configuracoes_gerais, "settings"), colors.TEXT_PRIMARY),
            (f"⇦  {self._t('logout')}", self._logout, colors.DANGER),
        ]

        for text, cmd, color in items:
            btn = ctk.CTkButton(
                self.profile_menu,
                text=text,
                fg_color="transparent",
                hover_color=colors.NEUTRAL_100,
                text_color=color,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),
                height=44,
                corner_radius=14,
                command=lambda c=cmd: [self._close_profile_menu(), c()] if c else self._close_profile_menu(),
            )
            btn.pack(fill="x", padx=12, pady=(0, 6))

        self.profile_menu_open = True

    def _close_profile_menu(self):
        if self.profile_menu_open:
            self.profile_menu.destroy()
            self.profile_menu_open = False

    def _logout(self):
        auth = AuthController("", "")
        auth.logout()
        Modal(self, "Logout", "Você foi desconectado com sucesso!", type="success")
        if self.on_logout:
            self.after(800, self.on_logout)

    def _get_greeting(self) -> str:
        h = datetime.now().hour
        if h < 12:
            return "Bom dia"
        if h < 18:
            return "Boa tarde"
        return "Boa noite"

    def atualizar_avatar(self, nova_key: str):
        try:
            url = f"https://coracao-em-patas.s3.amazonaws.com/{nova_key}?t={datetime.now().timestamp()}"
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()

            img_pil = Image.open(BytesIO(resp.content))
            img_round = self._create_circular_image(img_pil, (40, 40))
            ctk_img = ctk.CTkImage(light_image=img_round, size=(40, 40))
            self.avatar_image = ctk_img

            self.avatar_btn.configure(image=ctk_img, text=self.profile_button_text)
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")
            self.avatar_image = None
            self.avatar_btn.configure(text=self.profile_button_text, image=None) # Reseta para ícone padrão em caso de erro
