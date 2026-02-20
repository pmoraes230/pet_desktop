import customtkinter as ctk
from datetime import datetime
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading

# Controllers
from app.controllers.auth_controller import AuthController
from app.controllers.vet_controller import VetController
from app.controllers.pet_controller import PetController
from app.controllers.perfil_controller import FotoPerfil
from app.controllers.prontuario_controller import ProntuarioController
from app.services.s3_client import get_url_s3

# Módulos
from .modulo_pacientes import ModuloPacientes
from .modulo_financeiro import ModuloFinanceiro
from .modulo_configuracoes import ModuloConfiguracoes
from .modulo_agenda import ModuloAgenda
from .modulo_prontuario import ModuloProntuario
from .modulo_chat import ModuloChat

from app.views.modal import Modal
import app.core.colors as colors


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

        # Controllers
        self.vet_ctrl = VetController(self.user_id) if self.user_id else None
        self.pet_ctrl = PetController()
        self.prontuario_ctrl = ProntuarioController(self.user_id) if self.user_id else None
        self.foto_perfil_ctrl = FotoPerfil(self.user_id)

        # Estados UI
        self.profile_menu_open = False
        self.profile_menu = None
        self.notifications_open = False
        self.notifications_menu = None

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
        self.grid_rowconfigure(0, weight=0, minsize=76)   # um pouco mais alto
        self.grid_rowconfigure(1, weight=1)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=colors.PRIMARY_DARK,  # teal escuro sofisticado
            width=272,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo + nome
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(pady=(40, 48), padx=28, fill="x")

        logo = ctk.CTkImage(Image.open("app/assets/pet.png"), size=(40, 40))
        ctk.CTkLabel(header, image=logo, text="").pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            header,
            text="Coração em Patas",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="white",
        ).pack(side="left")

        # Navegação moderna
        nav_items = [
            ("Dashboard", self.show_dashboard, "home"),
            ("Mensagens", lambda: self.mod_chat.tela_chat(), "message-square"),
            ("Pacientes", lambda: self.mod_pacientes.tela_pacientes(), "paw"),
            ("Prontuários", lambda: self.mod_prontuario.tela_prontuario(), "file-text"),
            ("Agenda", lambda: self.mod_agenda.tela_agenda(), "calendar"),
            ("Financeiro", lambda: self.mod_financeiro.tela_financeiro(), "dollar-sign"),
        ]

        for label, command, icon_key in nav_items:
            self._create_sidebar_button(label, command, icon_key)

    def _create_sidebar_button(self, label: str, command, icon_key: str):
        icon_map = {
            "home": "🏠",
            "message-square": "💬",
            "paw": "🐾",
            "file-text": "📋",
            "calendar": "📅",
            "dollar-sign": "💰",
        }
        icon = icon_map.get(icon_key, "•")

        btn = ctk.CTkButton(
            self.sidebar,
            text=f"{icon}   {label}",
            fg_color="transparent",
            hover_color=colors.PRIMARY_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            height=52,
            corner_radius=14,
            anchor="w",
            command=lambda: self._switch_screen(command),
        )
        btn.pack(fill="x", padx=20, pady=6)

    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.topbar.grid(row=0, column=1, sticky="ew")
        
        # Remove qualquer borda cinza indesejada
        self.topbar.configure(border_width=0)

        # Saudação moderna
        greeting = f"{self._get_greeting()}, {self.user_name.split()[0]}"
        ctk.CTkLabel(
            self.topbar,
            text=greeting,
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(side="left", padx=40, pady=16)

        # Área direita com espaçamento maior
        right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right.pack(side="right", padx=32)

        # Notificações
        notif_frame = ctk.CTkFrame(right, fg_color="transparent", width=56, height=56)
        notif_frame.pack_propagate(False)
        notif_frame.pack(side="left", padx=(0, 24))

        self.btn_notif = ctk.CTkButton(
            notif_frame,
            text="🔔",
            font=("Segoe UI", 22),
            fg_color="transparent",
            hover_color=colors.NEUTRAL_100,
            text_color=colors.TEXT_SECONDARY,
            width=52,
            height=52,
            corner_radius=26,
            command=self._toggle_notifications,
        )
        self.btn_notif.pack()

        unread = self.vet_ctrl.fetch_unread_count() if self.vet_ctrl else 0
        self.badge = ctk.CTkLabel(
            notif_frame,
            text=str(unread) if unread else "",
            fg_color=colors.DANGER,
            text_color="white",
            width=22,
            height=22,
            corner_radius=11,
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
        )
        self.badge.place(relx=1.0, rely=0.0, anchor="ne")

        # Avatar moderno (circular com sombra sutil)
        self.avatar_btn = ctk.CTkButton(
            right,
            text="👤",
            font=("Segoe UI", 24),
            fg_color="transparent",
            hover_color=colors.NEUTRAL_100,
            text_color=colors.NEUTRAL_500,
            width=52,
            height=52,
            corner_radius=26,
            command=self._toggle_profile_menu,
        )
        self.avatar_btn.pack(side="left", padx=16)

        # Separador inferior sutil (opcional – pode remover se preferir sem linha)
        ctk.CTkFrame(self, fg_color="#E5E7EB", height=1).grid(
            row=0, column=1, sticky="sew"
        )

    def _build_content_frame(self):
        self.content = ctk.CTkFrame(self, fg_color=colors.NEUTRAL_50)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _init_modules(self):
        self.mod_pacientes     = ModuloPacientes(self.content, self.pet_ctrl)
        self.mod_financeiro    = ModuloFinanceiro(self.content)
        self.mod_configuracoes = ModuloConfiguracoes(self.content, parent=self)
        self.mod_agenda        = ModuloAgenda(self.content)
        self.mod_prontuario    = ModuloProntuario(self.content, self.prontuario_ctrl)
        self.mod_chat          = ModuloChat(self.content)

    def _switch_screen(self, target_screen_func):
        for child in self.content.winfo_children():
            child.destroy()
        target_screen_func()

    # ── Telas ────────────────────────────────────────────────────────────────

    def show_dashboard(self):
        self._switch_screen(self._build_dashboard_screen)

    def _build_dashboard_screen(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=40)

        scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="group1")

        metrics = self.vet_ctrl.fetch_metrics() if self.vet_ctrl else {}

        self._create_metric_card(
            scroll, metrics.get("total_pets", 0), "Pacientes cadastrados", "users", 0
        )
        self._create_metric_card(
            scroll, metrics.get("consultas_hoje", 0), "Consultas hoje", "calendar", 1
        )
        self._create_metric_card(
            scroll,
            metrics.get("faturamento_mes", 0),
            "Faturamento mensal",
            "dollar-sign",
            2,
            prefix="R$ ",
        )

        ctk.CTkLabel(
            scroll,
            text="Atendimentos Recentes",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(48, 20), padx=8)

        recent = self.vet_ctrl.fetch_recent_pets() if self.vet_ctrl else []
        self._build_recent_pets_list(scroll, recent)

    def _create_metric_card(self, parent, value, title, icon_key, col, prefix=""):
        icon_map = {"users": "👥", "calendar": "🗓️", "dollar-sign": "💰"}

        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color=colors.NEUTRAL_200,
        )
        card.grid(row=0, column=col, padx=16, pady=8, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=icon_map.get(icon_key, "•"),
            font=("Segoe UI", 36),
            text_color=colors.PRIMARY,
        ).pack(anchor="w", padx=32, pady=(28, 0))

        val_frame = ctk.CTkFrame(card, fg_color="transparent")
        val_frame.pack(fill="x", padx=32, pady=16)

        display_value = f"{prefix}{value:,}" if isinstance(value, (int, float)) else str(value)
        ctk.CTkLabel(
            val_frame,
            text=display_value,
            font=ctk.CTkFont(family="Helvetica", size=34, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Helvetica", size=15),
            text_color=colors.TEXT_SECONDARY,
        ).pack(anchor="w", padx=32, pady=(4, 28))

    def _build_recent_pets_list(self, parent, pets: list):
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color=colors.NEUTRAL_200,
        )
        card.grid(row=2, column=0, columnspan=2, padx=(0, 16), pady=12, sticky="nsew")

        if not pets:
            ctk.CTkLabel(
                card,
                text="Nenhum atendimento recente registrado",
                font=ctk.CTkFont(family="Helvetica", size=15),
                text_color=colors.TEXT_SECONDARY,
            ).pack(pady=60)
            return

        for pet in pets[:6]:
            self._create_pet_history_row(card, pet)

    def _create_pet_history_row(self, parent, pet: dict):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=14)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info,
            text=pet.get("nome_pet", "—"),
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"{pet.get('ESPECIE', '—')} • {pet.get('RACA', '—')}",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY,
        ).pack(anchor="w")

        status = ctk.CTkLabel(
            row,
            text="Atendido",
            text_color=colors.SUCCESS,
            fg_color=colors.SUCCESS_BG,
            corner_radius=10,
            padx=16,
            pady=8,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        )
        status.pack(side="right")

    # ── Avatar ───────────────────────────────────────────────────────────────

    def _load_avatar_background(self):
        try:
            perfil = self.foto_perfil_ctrl.fetch_perfil_data()
            key = perfil.get("imagem_perfil_veterinario")
            if not key:
                return

            url = get_url_s3(key, expires_in=604800)
            if not url:
                return

            session = requests.Session()
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
            session.mount("https://", HTTPAdapter(max_retries=retries))

            resp = session.get(url, timeout=10)
            resp.raise_for_status()

            img_pil = Image.open(BytesIO(resp.content))
            img_round = self._create_circular_image(img_pil, (52, 52))

            ctk_img = ctk.CTkImage(light_image=img_round, size=(52, 52))

            self.after(0, lambda img=ctk_img: self.avatar_btn.configure(image=img, text=""))

        except Exception as e:
            print(f"Falha ao carregar avatar: {e}")

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
        if self.notifications_open:
            if self.notifications_menu and self.notifications_menu.winfo_exists():
                self.notifications_menu.destroy()
            self.notifications_open = False
            return

        if self.profile_menu_open:
            self._toggle_profile_menu()

        self.notifications_menu = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color=colors.NEUTRAL_200
        )
        self.notifications_menu.place(relx=0.98, y=76, anchor="ne")

        ctk.CTkLabel(
            self.notifications_menu,
            text="Notificações",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(pady=16, padx=24, anchor="w")

        scroll = ctk.CTkScrollableFrame(self.notifications_menu, fg_color="transparent", height=300)
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        notifications = self.vet_ctrl.fetch_alerts() if self.vet_ctrl else []

        if not notifications:
            ctk.CTkLabel(
                scroll,
                text="Nenhuma notificação no momento",
                font=ctk.CTkFont(family="Helvetica", size=14),
                text_color=colors.TEXT_SECONDARY,
            ).pack(pady=60)
        else:
            for notif in notifications:
                self._create_notification_item(
                    scroll,
                    notif.get("tipo", "Notificação"),
                    notif.get("mensagem", ""),
                    notif.get("id"),
                    bool(notif.get("lida", False)),
                )

        self.notifications_open = True

    def _create_notification_item(self, parent, title, message, notif_id=None, read=False):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", padx=16, pady=8)

        title_lbl = ctk.CTkLabel(
            item,
            text=title,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=colors.TEXT_PRIMARY if not read else colors.TEXT_SECONDARY,
        )
        title_lbl.pack(anchor="w")

        msg_lbl = ctk.CTkLabel(
            item,
            text=message,
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color=colors.TEXT_SECONDARY if read else colors.TEXT_PRIMARY,
            wraplength=280,
            justify="left",
        )
        msg_lbl.pack(anchor="w", pady=(4, 0))

        def mark_as_read(event=None):
            if notif_id and self.vet_ctrl:
                try:
                    self.vet_ctrl.mark_notification_read(notif_id)
                    title_lbl.configure(text_color=colors.TEXT_SECONDARY)
                    msg_lbl.configure(text_color=colors.TEXT_SECONDARY)
                    unread = self.vet_ctrl.fetch_unread_count() or 0
                    self.badge.configure(text=str(unread) if unread > 0 else "")
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
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color=colors.NEUTRAL_200
        )
        self.profile_menu.place(relx=0.98, y=76, anchor="ne")

        items = [
            ("Editar Perfil", self.mod_configuracoes.tela_configuracoes_perfil),
            ("Configurações", self.mod_configuracoes.tela_configuracoes_gerais),
            ("Sair", self._logout),
        ]

        for text, cmd in items:
            color = colors.DANGER if text == "Sair" else colors.TEXT_PRIMARY
            btn = ctk.CTkButton(
                self.profile_menu,
                text=text,
                fg_color="transparent",
                hover_color=colors.NEUTRAL_100,
                text_color=color,
                anchor="w",
                font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                height=42,
                command=lambda c=cmd: [self._close_profile_menu(), c()] if c else self._close_profile_menu(),
            )
            btn.pack(fill="x", padx=12, pady=4)

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
            img_round = self._create_circular_image(img_pil, (52, 52))
            ctk_img = ctk.CTkImage(light_image=img_round, size=(52, 52))

            self.avatar_btn.configure(image=ctk_img, text="")
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")