import customtkinter as ctk
from tkinter import filedialog
from io import BytesIO
from PIL import Image, ImageDraw
import boto3

# Seus imports existentes...
from ..services.s3_client import upload_foto_s3
from ..config.database import connectdb
from app.models.mudar_foto import salvar_nova_foto
from app.views.modal import Modal  # se tiver

# Cores e estilos constantes para consistência
COLOR_PRIMARY = "#14B8A6"
COLOR_HOVER = "#0EA47A"
COLOR_TEXT = "#1E293B"
COLOR_GRAY = "#64748B"
COLOR_BORDER = "#E2E8F0"
FONT_TITLE = ("Arial", 24, "bold")
FONT_SUBTITLE = ("Arial", 16, "bold")
FONT_LABEL = ("Arial", 12, "bold")
FONT_INPUT = ("Arial", 13)

# Função auxiliar (já existia)
def criar_imagem_redonda(pil_img, size):
    pil_img = pil_img.resize(size).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(pil_img, (0, 0), mask)
    return output


class ModuloConfiguracoes:
    def __init__(self, content_frame, current_user_id=None, foto_perfil=None, callback_atualizar_avatar=None):
        self.content = content_frame
        self.current_user_id = current_user_id
        self.foto_perfil = foto_perfil
        self.callback_atualizar_avatar = callback_atualizar_avatar

        self.preview_img = None

    def _limpar_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _criar_container_principal(self):
        """Cria o container que ocupa todo o espaço do content com grid"""
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        return container

    # ────────────────────────────────────────────────
    # TELA: EDITAR PERFIL
    # ────────────────────────────────────────────────
    def tela_configuracoes_perfil(self):
        self._limpar_content()
        container = self._criar_container_principal()

        scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            orientation="vertical"
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=35, pady=25)

        # Título
        ctk.CTkLabel(
            scroll,
            text="Editar Perfil Profissional",
            font=("Arial", 26, "bold"),
            text_color="#0F172A"
        ).pack(anchor="w", pady=(0, 35))

        # Card Foto
        card_foto = ctk.CTkFrame(scroll, fg_color="white", corner_radius=16, border_width=1, border_color="#E2E8F0")
        card_foto.pack(fill="x", pady=(0, 25), ipady=20)

        foto_row = ctk.CTkFrame(card_foto, fg_color="transparent")
        foto_row.pack(pady=15, padx=30)

        # Avatar
        avatar_container = ctk.CTkFrame(
            foto_row,
            width=140, height=140,
            corner_radius=70,
            fg_color="#F1F5F9",
            border_width=4,
            border_color="#14B8A6"
        )
        avatar_container.pack(side="left", padx=(0, 40))
        avatar_container.pack_propagate(False)

        self.avatar_label = ctk.CTkLabel(
            avatar_container,
            text="U",
            font=("Arial", 55, "bold"),
            text_color="#14B8A6"
        )
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        # Botão alterar foto
        btn_foto = ctk.CTkButton(
            foto_row,
            text="Alterar foto",
            image=ctk.CTkImage(light_image=None, size=(20,20)),  # pode adicionar ícone
            compound="left",
            fg_color="#14B8A6",
            hover_color="#0EA47A",
            corner_radius=10,
            height=42,
            command=self.escolher_nova_foto
        )
        btn_foto.pack(side="left", pady=10)

        # Carregar foto atual
        self.carregar_foto_atual()

        # Card Dados
        card_dados = ctk.CTkFrame(scroll, fg_color="white", corner_radius=16, border_width=1, border_color="#E2E8F0")
        card_dados.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(
            card_dados,
            text="Informações Profissionais",
            font=("Arial", 18, "bold"),
            text_color="#0F172A"
        ).pack(anchor="w", padx=30, pady=(25, 15))

        form_frame = ctk.CTkFrame(card_dados, fg_color="transparent")
        form_frame.pack(fill="x", padx=30, pady=(0, 30))
        form_frame.columnconfigure((0, 1), weight=1)

        # Campos (exemplo - você pode carregar valores reais depois)
        self.criar_campo_input(form_frame, "Nome completo", "Patrick Silva", 0, 0)
        self.criar_campo_input(form_frame, "E-mail", "seuemail@exemplo.com", 0, 1)
        self.criar_campo_input(form_frame, "CRMV", "12345-SP", 1, 0)
        self.criar_campo_input(form_frame, "Estado (UF)", "São Paulo", 1, 1)

        # Botão salvar
        btn_salvar = ctk.CTkButton(
            card_dados,
            text="Salvar Alterações",
            fg_color="#14B8A6",
            hover_color="#0EA47A",
            corner_radius=10,
            height=48,
            font=("Arial", 15, "bold"),
            command=self.salvar_perfil  # crie este método depois
        )
        btn_salvar.pack(pady=(0, 30), padx=30, anchor="e")

    def carregar_foto_atual(self):
        if not self.foto_perfil:
            return

        try:
            perfil = self.foto_perfil.fetch_perfil_data()
            key = perfil.get("imagem_perfil_veterinario")
            if key:
                s3 = boto3.client("s3")
                obj = s3.get_object(Bucket="coracao-em-patas", Key=key)
                img = Image.open(BytesIO(obj["Body"].read()))
                img = criar_imagem_redonda(img, (136, 136))
                self.preview_img = ctk.CTkImage(light_image=img, size=(136, 136))
                self.avatar_label.configure(image=self.preview_img, text="")
                self.avatar_label.image = self.preview_img  # mantém referência
        except Exception as e:
            print("Erro ao carregar foto:", e)

    def escolher_nova_foto(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")])
        if not caminho:
            return

        try:
            nova_key = salvar_nova_foto(self.current_user_id, caminho)
            if nova_key:
                self.atualizar_preview_foto(caminho)
                if self.callback_atualizar_avatar:
                    self.callback_atualizar_avatar(nova_key)
                Modal(self.content.master, "Sucesso", "Foto atualizada com sucesso!", type="success")
        except Exception as e:
            Modal(self.content.master, "Erro", f"Não foi possível atualizar a foto.\n{e}", type="error")

    def atualizar_preview_foto(self, caminho_arquivo):
        img = Image.open(caminho_arquivo)
        img = criar_imagem_redonda(img, (136, 136))
        self.preview_img = ctk.CTkImage(light_image=img, size=(136, 136))
        self.avatar_label.configure(image=self.preview_img, text="")
        self.avatar_label.image = self.preview_img

    def criar_campo_input(self, master, titulo, valor_inicial, linha, coluna):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=linha, column=coluna, padx=12, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text=titulo.upper(),
            font=("Arial", 11, "bold"),
            text_color="#64748B"
        ).pack(anchor="w", pady=(0, 6))

        entry = ctk.CTkEntry(
            frame,
            height=46,
            corner_radius=10,
            border_width=0,
            fg_color="#F8FAFC",
            text_color="#0F172A",
            font=("Arial", 14)
        )
        entry.insert(0, valor_inicial)
        entry.pack(fill="x")
        return entry

    def salvar_perfil(self):
        # Implementar salvamento real aqui
        Modal(self.content.master, "Sucesso", "Perfil atualizado com sucesso!", type="success")

    # ────────────────────────────────────────────────────────────────
    # TELA: CONFIGURAÇÕES GERAIS
    # ────────────────────────────────────────────────────────────────
    def tela_configuracoes_gerais(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        main_container = ctk.CTkFrame(self.content, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=40, pady=20)

        ctk.CTkLabel(scroll, text="Configurações da Conta", font=FONT_TITLE, text_color=COLOR_TEXT).pack(anchor="w", pady=(0, 30))

        # ── Card Idioma ──
        lang_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        lang_card.pack(fill="x", pady=10)

        ctk.CTkLabel(lang_card, text="🌐 Idioma", font=FONT_SUBTITLE, text_color=COLOR_TEXT).pack(side="left", padx=20, pady=20)
        ctk.CTkOptionMenu(
            lang_card,
            values=["Português", "English", "Español"],
            fg_color="#F8FAFC",
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_HOVER,
            text_color=COLOR_TEXT
        ).pack(side="right", padx=20)

        # ── Card Notificações ──
        notif_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        notif_card.pack(fill="x", pady=10)

        ctk.CTkLabel(notif_card, text="🔔 Notificações", font=FONT_SUBTITLE, text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=20)

        for label in ["E-mail", "Lembretes", "Dicas semanais"]:
            row = ctk.CTkFrame(notif_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=label, font=FONT_LABEL, text_color=COLOR_GRAY).pack(side="left")
            switch = ctk.CTkSwitch(row, onvalue=True, offvalue=False, progress_color=COLOR_PRIMARY)
            switch.pack(side="right")

        # ── Card Segurança ──
        security_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        security_card.pack(fill="x", pady=10)

        ctk.CTkLabel(security_card, text="🔒 Segurança da Conta", font=FONT_SUBTITLE, text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(security_card, text="Atualize sua senha para maior segurança.", font=("Arial", 12), text_color=COLOR_GRAY).pack(anchor="w", padx=20, pady=(0, 20))

        change_pwd_btn = ctk.CTkButton(
            security_card,
            text="Alterar Senha",
            font=FONT_LABEL,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_HOVER,
            corner_radius=12,
            height=45,
            command=self.tela_alterar_senha
        )
        change_pwd_btn.pack(anchor="w", padx=20, pady=(0, 20))

        # ── Card Desativar Conta ──
        danger_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#FCA5A5")
        danger_card.pack(fill="x", pady=20)

        ctk.CTkLabel(danger_card, text="⚠️ Desativar Conta", font=FONT_SUBTITLE, text_color="#EF4444").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(danger_card, text="Essa ação é irreversível.", font=("Arial", 12), text_color=COLOR_GRAY).pack(anchor="w", padx=20, pady=(0, 20))

        deactivate_btn = ctk.CTkButton(
            danger_card,
            text="Desativar Conta",
            font=FONT_LABEL,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=12,
            height=45,
            command=self._confirmar_desativacao
        )
        deactivate_btn.pack(anchor="w", padx=20, pady=(0, 20))

    def tela_alterar_senha(self):
        # Limpar e criar tela de alterar senha
        for widget in self.content.winfo_children():
            widget.destroy()

        main_container = ctk.CTkFrame(self.content, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=40, pady=20)

        ctk.CTkLabel(scroll, text="Alterar Senha", font=FONT_TITLE, text_color=COLOR_TEXT).pack(anchor="w", pady=(0, 30))

        # Card Senha
        senha_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        senha_card.pack(fill="x", pady=20)

        form_grid = ctk.CTkFrame(senha_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=30, pady=30)
        form_grid.columnconfigure(0, weight=1)

        old_pwd = self._create_input_field(form_grid, "Senha Atual", "", 0, 0, show="*")
        new_pwd = self._create_input_field(form_grid, "Nova Senha", "", 1, 0, show="*")
        confirm_pwd = self._create_input_field(form_grid, "Confirmar Nova Senha", "", 2, 0, show="*")

        save_btn = ctk.CTkButton(
            senha_card,
            text="Atualizar Senha",
            font=FONT_LABEL,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_HOVER,
            corner_radius=12,
            height=45,
            command=lambda: self._atualizar_senha(old_pwd.get(), new_pwd.get(), confirm_pwd.get())
        )
        save_btn.pack(pady=20, padx=30, anchor="e")

        back_btn = ctk.CTkButton(
            senha_card,
            text="Voltar",
            font=FONT_LABEL,
            fg_color="#64748B",
            hover_color="#475569",
            corner_radius=12,
            height=45,
            command=self.tela_configuracoes_gerais
        )
        back_btn.pack(pady=(0, 20), padx=30, anchor="e")

    def _atualizar_senha(self, old, new, confirm):
        if new != confirm:
            Modal(self.content, "Erro", "As senhas não coincidem.", type="error")
            return
        if len(new) < 8:
            Modal(self.content, "Erro", "A senha deve ter pelo menos 8 caracteres.", type="error")
            return

        try:
            # Implemente com self.vet_controller.update_password(old, new)
            Modal(self.content, "Sucesso", "Senha atualizada com sucesso!", type="success")
            self.tela_configuracoes_gerais()
        except Exception as e:
            Modal(self.content, "Erro", f"Erro ao atualizar senha: {str(e)}", type="error")

    def _confirmar_desativacao(self):
        # Modal de confirmação
        if messagebox.askyesno("Confirmação", "Tem certeza que deseja desativar a conta? Essa ação é irreversível."):
            try:
                # Implemente com self.vet_controller.deactivate_account()
                Modal(self.content, "Sucesso", "Conta desativada. Você será desconectado.", type="info")
                # Chame logout se necessário
            except Exception as e:
                Modal(self.content, "Erro", f"Erro ao desativar conta: {str(e)}", type="error")

    # ────────────────────────────────────────────────────────────────
    # AUXILIARES
    # ────────────────────────────────────────────────────────────────
    def mostrar_modal(self, title, message, type="info"):
        # Use seu Modal customizado
        Modal(self.content, title, message, type=type)