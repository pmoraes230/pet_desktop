import customtkinter as ctk
from tkinter import filedialog
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from app.utils.loading_overlay import run_with_loading
from ..services.s3_client import get_url_s3
from app.models.mudar_foto import salvar_nova_foto
from ..controllers.veterinario_controller import vetController
from app.config.database import connectdb
from app.core.i18n import get_language, tr
from django.contrib.auth.hashers import check_password, make_password

def criar_imagem_redonda(pil_img, size):
    # Para o novo layout, o arredondamento é menor (corner_radius alto, mas não círculo perfeito)
    pil_img = pil_img.resize(size).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + size, radius=30, fill=255) # Cantos arredondados estilo modern
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(pil_img, (0, 0), mask)
    return output

class ModuloConfiguracoes:
    def __init__(self, content_frame=None, parent=None, on_avatar_updated=None):
        self.content = content_frame
        self.parent = parent
        self.on_avatar_updated = on_avatar_updated 
        self.current_user_id = self._get_user_id()
        self.vet_ctrl = vetController(self.current_user_id) if self.current_user_id else None
        
        self.perfil_data = None
        self.foto_key = None
        self.preview_img = None
        self._carregar_dados_perfil()

    def _get_user_id(self):
        if self.parent and hasattr(self.parent, "current_user"):
            user = self.parent.current_user
            if isinstance(user, dict):
                return user.get("id") or user.get("ID") or user.get("veterinario_id")
        return None

    # --- TELA PRINCIPAL DE PERFIL (IGUAL A SEGUNDA IMAGEM) ---
    def tela_visualizar_perfil(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        # Fundo levemente cinza/azulado como no design moderno
        self.content.configure(fg_color="#F8FAFC")

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)

        # --- 1. CARD SUPERIOR (HEADER) ---
        header_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=30, border_width=1, border_color="#E2E8F0")
        header_card.pack(fill="x", pady=(0, 20))

        inner_h = ctk.CTkFrame(header_card, fg_color="transparent")
        inner_h.pack(padx=30, pady=30, fill="x")

        # Foto (Lado Esquerdo)
        self.renderizar_foto_perfil(inner_h)

        # Informações (Centro)
        info_f = ctk.CTkFrame(inner_h, fg_color="transparent")
        info_f.pack(side="left", padx=30, fill="y")

        nome_f = ctk.CTkFrame(info_f, fg_color="transparent")
        nome_f.pack(anchor="w")
        
        ctk.CTkLabel(nome_f, text=self.perfil_data.get("nome", self._t("Usuário")), 
                     font=("Helvetica", 32, "bold"), text_color="#1E293B").pack(side="left")
        
        # Badge de Verificado
        badge = ctk.CTkFrame(nome_f, fg_color="#CCF2ED", corner_radius=10)
        badge.pack(side="left", padx=15)
        ctk.CTkLabel(badge, text=self._t("MÉDICO VERIFICADO"), font=("Helvetica", 10, "bold"), text_color="#14B8A6").pack(padx=10, pady=2)

        ctk.CTkLabel(info_f, text=f"CRMV {self.perfil_data.get('CRMV', '---')} / {self.perfil_data.get('UF_CRMV', '---')}", 
                     font=("Helvetica", 16), text_color="#94A3B8").pack(anchor="w", pady=(0, 15))

        # Pílulas de Contato
        contact_f = ctk.CTkFrame(info_f, fg_color="transparent")
        contact_f.pack(anchor="w")
        self.criar_pill_contato(contact_f, "✉", self.perfil_data.get("email", "---"))
        self.criar_pill_contato(contact_f, "📞", "Não informado")

        # Botão Editar (Canto Superior Direito)
        ctk.CTkButton(inner_h, text=f"✎  {self._t('EDITAR')}", fg_color="#14B8A6", hover_color="#0D9488", 
                      width=130, height=45, corner_radius=15, font=("Helvetica", 13, "bold"),
                      command=self.tela_configuracoes_perfil).pack(side="right", anchor="n")

        # --- 2. LINHA DO MEIO (COLUNAS) ---
        mid_row = ctk.CTkFrame(scroll, fg_color="transparent")
        mid_row.pack(fill="x", pady=10)
        mid_row.grid_columnconfigure(0, weight=1)
        mid_row.grid_columnconfigure(1, weight=1)

        # Card: Atuação Profissional
        at_card = ctk.CTkFrame(mid_row, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        at_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(at_card, text=f"🛡  {self._t('Atuação Profissional')}", font=("Helvetica", 18, "bold"), text_color="#1E293B").pack(anchor="w", padx=25, pady=20)
        self.criar_linha_info(at_card, self._t("INSCRIÇÃO CRMV"), self.perfil_data.get("CRMV", "---"))
        self.criar_linha_info(at_card, self._t("ESTADO (UF)"), self.perfil_data.get("UF_CRMV", "---"))
        self.criar_linha_info(at_card, self._t("MÉDIA DE AVALIAÇÕES"), "⭐ 5.0")

        # Card: Estatísticas
        st_card = ctk.CTkFrame(mid_row, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        st_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        ctk.CTkLabel(st_card, text=f"📈  {self._t('Estatísticas')}", font=("Helvetica", 18, "bold"), text_color="#1E293B").pack(anchor="w", padx=25, pady=20)
        
        st_cont = ctk.CTkFrame(st_card, fg_color="transparent")
        st_cont.pack(fill="x", padx=20, pady=10)
        self.criar_box_estatistica(st_cont, "0", self._t("Pacientes").upper())
        self.criar_box_estatistica(st_cont, "0", self._t("CONSULTAS"))

        # --- 3. CARD INFERIOR (PRIVACIDADE) ---
        priv_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        priv_card.pack(fill="x", pady=20)
        
        ctk.CTkLabel(priv_card, text=f"🛡  {self._t('Privacidade e Acesso')}", font=("Helvetica", 18, "bold"), text_color="#1E293B").pack(anchor="w", padx=25, pady=20)
        
        btns_f = ctk.CTkFrame(priv_card, fg_color="transparent")
        btns_f.pack(fill="x", padx=25, pady=(0, 25))
        
        ctk.CTkButton(btns_f, text=self._t("ALTERAR MINHA SENHA"), fg_color="white", text_color="#1E293B", border_width=1, border_color="#E2E8F0", height=50, corner_radius=15, font=("Helvetica", 12, "bold"), command=self.tela_alterar_senha).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns_f, text=self._t("SAIR DA CONTA"), fg_color="#FEF2F2", text_color="#EF4444", hover_color="#FEE2E2", height=50, corner_radius=15, font=("Helvetica", 12, "bold")).pack(side="left", expand=True, fill="x", padx=(10, 0))

    # --- WIDGETS AUXILIARES ---
    def criar_pill_contato(self, master, icon, text):
        pill = ctk.CTkFrame(master, fg_color="#F1F5F9", corner_radius=10)
        pill.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(pill, text=f"{icon}  {text}", font=("Helvetica", 12), text_color="#475569").pack(padx=15, pady=5)

    def criar_linha_info(self, master, label, value):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(f, text=label, font=("Helvetica", 12, "bold"), text_color="#94A3B8").pack(side="left")
        ctk.CTkLabel(f, text=value, font=("Helvetica", 14, "bold"), text_color="#1E293B").pack(side="right")

    def criar_box_estatistica(self, master, value, label):
        box = ctk.CTkFrame(master, fg_color="#F8FAFC", corner_radius=20, height=120)
        box.pack(side="left", expand=True, fill="x", padx=10)
        box.pack_propagate(False)
        ctk.CTkLabel(box, text=value, font=("Helvetica", 36, "bold"), text_color="#1E293B").pack(pady=(20, 0))
        ctk.CTkLabel(box, text=label, font=("Helvetica", 11, "bold"), text_color="#94A3B8").pack()

    def renderizar_foto_perfil(self, master):
        size = (140, 140)
        av_f = ctk.CTkFrame(master, width=size[0], height=size[1], corner_radius=35, fg_color="#F1F5F9")
        av_f.pack(side="left")
        av_f.pack_propagate(False)
        
        self.avatar_label = ctk.CTkLabel(av_f, text="👤", font=("Arial", 50))
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        if self.foto_key:
            try:
                url = get_url_s3(self.foto_key)
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))
                img_r = criar_imagem_redonda(img, size)
                img_ctk = ctk.CTkImage(light_image=img_r, size=size)
                self.avatar_label.configure(image=img_ctk, text="")
                self.avatar_label.image = img_ctk
            except: pass

    # --- MANTÉM OS MÉTODOS ORIGINAIS DE CARREGAMENTO E EDIÇÃO ---
    def _carregar_dados_perfil(self):
        if self.vet_ctrl:
            dados = self.vet_ctrl.fetch_perfil_data()
            if dados:
                self.perfil_data = dados
                self.foto_key = dados.get('imagem_perfil_veterinario')

    # Alias/handlers para compatibilidade com o dashboard
    def tela_configuracoes_perfil(self):
        """Compatibilidade: abre a tela de visualização/edição do perfil."""
        return self.tela_visualizar_perfil()

    def tela_configuracoes_gerais(self):
        """Tela de configurações gerais (idioma, notificações e privacidade)."""
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="#F8FAFC")
        scroll.pack(fill="both", expand=True)

        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(pady=40, padx=100, fill="x")

        title_f = ctk.CTkFrame(container, fg_color="transparent")
        title_f.pack(fill="x", pady=(0, 30))
        ctk.CTkLabel(title_f, text=self._t("account_settings"), font=("Helvetica", 24, "bold"), text_color="#1E293B").pack(side="left")

        # Cards de Configuração (simples e funcionais)
        def _card(master, icon, icon_bg, title, sub, dropdown=False, checks=None, arrow_btn=None):
            card = ctk.CTkFrame(master, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
            card.pack(fill="x", pady=10)
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=20)
            icon_f = ctk.CTkFrame(header, width=45, height=45, corner_radius=12, fg_color=icon_bg)
            icon_f.pack(side="left"); icon_f.pack_propagate(False)
            ctk.CTkLabel(icon_f, text=icon, font=("Helvetica", 18)).place(relx=0.5, rely=0.5, anchor="center")
            txt_f = ctk.CTkFrame(header, fg_color="transparent")
            txt_f.pack(side="left", padx=15)
            ctk.CTkLabel(txt_f, text=title, font=("Helvetica", 15, "bold")).pack(anchor="w")
            ctk.CTkLabel(txt_f, text=sub, font=("Helvetica", 12), text_color="#94A3B8").pack(anchor="w")
            if dropdown:
                language_menu = ctk.CTkOptionMenu(
                    header,
                    values=["Português (Brasil)", "English"],
                    fg_color="#F8FAFC",
                    text_color="#1E293B",
                    button_color="#F1F5F9",
                    corner_radius=10,
                    command=self._on_language_selected,
                )
                language_menu.set("English" if self._language() == "en" else "Português (Brasil)")
                language_menu.pack(side="right")
            if checks:
                for c in checks:
                    row = ctk.CTkFrame(card, fg_color="#F8FAFC", corner_radius=10)
                    row.pack(fill="x", padx=20, pady=5)
                    ctk.CTkLabel(row, text=c, font=("Helvetica", 12)).pack(side="left", padx=15, pady=10)
                    cb = ctk.CTkCheckBox(row, text="", width=20)
                    cb.pack(side="right", padx=15); cb.select()
            if arrow_btn:
                btn = ctk.CTkButton(card, text=arrow_btn + "  ›", fg_color="transparent", text_color="#1E293B", anchor="w", hover_color="#F8FAFC", height=40)
                # Wire the 'Alterar senha' action to the password screen
                if arrow_btn in (self._t("change_password"), "Alterar senha", "Change password"):
                    btn.configure(command=self.tela_alterar_senha)
                btn.pack(fill="x", padx=20, pady=(0, 15))

        _card(container, "🌐", "#DBEAFE", self._t("language"), self._t("language_subtitle"), dropdown=True)
        _card(
            container,
            "🔔",
            "#F3E8FF",
            self._t("notifications"),
            self._t("notifications_subtitle"),
            checks=[self._t("email_notifications"), self._t("appointment_reminders"), self._t("exam_alerts")],
        )
        _card(container, "🛡", "#FEF3C7", self._t("privacy"), self._t("privacy_subtitle"), arrow_btn=self._t("change_password"))

        # Danger Zone
        danger = ctk.CTkFrame(container, fg_color="#FEF2F2", corner_radius=20, border_width=1, border_color="#FCA5A5")
        danger.pack(fill="x", pady=20)
        d_inner = ctk.CTkFrame(danger, fg_color="transparent")
        d_inner.pack(padx=25, pady=20, fill="x")
        icon_f = ctk.CTkFrame(d_inner, width=40, height=40, corner_radius=10, fg_color="#FEE2E2")
        icon_f.pack(side="left"); icon_f.pack_propagate(False)
        ctk.CTkLabel(icon_f, text="⚠️", text_color="#EF4444").place(relx=0.5, rely=0.5, anchor="center")
        txt_f = ctk.CTkFrame(d_inner, fg_color="transparent")
        txt_f.pack(side="left", padx=15)
        ctk.CTkLabel(txt_f, text=self._t("danger_zone"), font=("Helvetica", 14, "bold"), text_color="#991B1B").pack(anchor="w")
        ctk.CTkLabel(txt_f, text=self._t("deactivate_warning"), font=("Helvetica", 12), text_color="#B91C1C").pack(anchor="w")
        ctk.CTkButton(danger, text=self._t("deactivate_account"), fg_color="#EF4444", hover_color="#DC2626", height=45, corner_radius=12, font=("Helvetica", 12, "bold")).pack(fill="x", padx=25, pady=(0, 20))

    def _language(self):
        return getattr(self.parent, "language", get_language()) if self.parent else get_language()

    def _on_language_selected(self, selected):
        new_language = "en" if selected == "English" else "pt"
        if self.parent and hasattr(self.parent, "set_language"):
            self.parent.set_language(new_language)
        self.tela_configuracoes_gerais()

    def _t(self, key):
        local_translations = {
            "pt": {
                "account_settings": "⚙ Configurações da Conta",
                "language": "Idioma",
                "language_subtitle": "Escolha o idioma da plataforma",
                "notifications": "Notificações",
                "notifications_subtitle": "Gerencie seus alertas",
                "email_notifications": "Notificações por e-mail",
                "appointment_reminders": "Lembretes de consultas",
                "exam_alerts": "Alertas de exames",
                "privacy": "Privacidade",
                "privacy_subtitle": "Controle o acesso à sua conta",
                "change_password": "Alterar senha",
                "danger_zone": "Zona de Perigo",
                "deactivate_warning": "Ao desativar sua conta, você perderá acesso aos dados. Essa ação é irreversível.",
                "deactivate_account": "DESATIVAR MINHA CONTA",
            },
            "en": {
                "account_settings": "⚙ Account Settings",
                "language": "Language",
                "language_subtitle": "Choose the platform language",
                "notifications": "Notifications",
                "notifications_subtitle": "Manage your alerts",
                "email_notifications": "Email notifications",
                "appointment_reminders": "Appointment reminders",
                "exam_alerts": "Exam alerts",
                "privacy": "Privacy",
                "privacy_subtitle": "Control access to your account",
                "change_password": "Change password",
                "danger_zone": "Danger Zone",
                "deactivate_warning": "If you deactivate your account, you will lose access to your data. This action is irreversible.",
                "deactivate_account": "DEACTIVATE MY ACCOUNT",
            },
        }
        return local_translations.get(self._language(), local_translations["pt"]).get(key, tr(key))

    # Você deve chamar `self.tela_visualizar_perfil()` para ver a nova interface.

    # --- ALTERAR SENHA ---
    def tela_alterar_senha(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.content, fg_color="#F8FAFC")
        frame.pack(fill="both", expand=True, padx=40, pady=30)

        title = ctk.CTkLabel(frame, text=self._t("Alterar minha senha"), font=("Helvetica", 18, "bold"), text_color="#1E293B")
        title.pack(anchor="w", pady=(0, 16))

        form = ctk.CTkFrame(frame, fg_color="white", corner_radius=14, border_width=1, border_color="#E2E8F0")
        form.pack(fill="x", expand=False)
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(padx=18, pady=18, fill="x")

        ctk.CTkLabel(inner, text=self._t("Senha atual"), font=("Helvetica", 11, "bold"), text_color="#475569").pack(anchor="w")
        self._current_pwd = ctk.CTkEntry(inner, placeholder_text="••••••••", show="•", height=36, corner_radius=8)
        self._current_pwd.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text=self._t("Nova senha"), font=("Helvetica", 11, "bold"), text_color="#475569").pack(anchor="w")
        self._new_pwd = ctk.CTkEntry(inner, placeholder_text=self._t("Mínimo 8 caracteres"), show="•", height=36, corner_radius=8)
        self._new_pwd.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text=self._t("Confirmar nova senha"), font=("Helvetica", 11, "bold"), text_color="#475569").pack(anchor="w")
        self._confirm_pwd = ctk.CTkEntry(inner, placeholder_text=self._t("Repita a nova senha"), show="•", height=36, corner_radius=8)
        self._confirm_pwd.pack(fill="x", pady=(4, 8))

        self._pwd_msg = ctk.CTkLabel(inner, text="", font=("Helvetica", 10), text_color="#DC2626")
        self._pwd_msg.pack(anchor="w", pady=(4, 12))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(btns, text=self._t("CANCELAR"), fg_color="#F1F5F9", text_color="#475569", height=36, corner_radius=8, font=("Helvetica", 11, "bold"), command=self.tela_configuracoes_gerais).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text=self._t("SALVAR"), fg_color="#14B8A6", text_color="white", height=36, corner_radius=8, font=("Helvetica", 11, "bold"), command=self._on_submit_change_password).pack(side="right", expand=True, fill="x")

    def _on_submit_change_password(self):
        cur = self._current_pwd.get().strip()
        new = self._new_pwd.get().strip()
        conf = self._confirm_pwd.get().strip()

        # Basic validation
        if not cur or not new or not conf:
            self._pwd_msg.configure(text=self._t("Preencha todos os campos"))
            return
        if len(new) < 8:
            self._pwd_msg.configure(text=self._t("A nova senha deve ter ao menos 8 caracteres"))
            return
        if new != conf:
            self._pwd_msg.configure(text=self._t("As senhas não coincidem"))
            return

        # Run update with loading
        run_with_loading(self._change_password_backend, self._t("Atualizando senha..."), cur, new)

    def _change_password_backend(self, current_password, new_password):
        # Verifica usuário atual
        if not self.current_user_id:
            self.content.after(0, lambda: self._pwd_msg.configure(text=self._t("Usuário não encontrado")))
            return

        try:
            conn = connectdb()
            cursor = conn.cursor()
            # Busca hash atual
            cursor.execute("SELECT senha_veterinario FROM veterinario WHERE id = %s", (self.current_user_id,))
            row = cursor.fetchone()
            if not row:
                self.content.after(0, lambda: self._pwd_msg.configure(text=self._t("Usuário não encontrado")))
                return

            stored_hash = row[0]
            if not check_password(current_password, stored_hash):
                self.content.after(0, lambda: self._pwd_msg.configure(text=self._t("Senha atual incorreta")))
                return

            # Gerar hash da nova senha e atualizar
            new_hash = make_password(new_password)
            cursor.execute("UPDATE veterinario SET senha_veterinario = %s WHERE id = %s", (new_hash, self.current_user_id))
            conn.commit()
            cursor.close(); conn.close()

            # Success -> volta para gerais com mensagem
            def _on_success():
                self.tela_configuracoes_gerais()
            self.content.after(0, _on_success)

        except Exception as e:
            print(f"Erro ao alterar senha: {e}")
            try:
                cursor.close()
                conn.close()
            except:
                pass
            self.content.after(0, lambda: self._pwd_msg.configure(text=self._t("Erro ao atualizar senha")))
