import customtkinter as ctk
import webbrowser
from app.widgets.modal import Modal
import app.core.colors as colors   # suas cores personalizadas

# Endereço para criar conta (abre no navegador)
CADASTRO_URL = "http://127.0.0.1:8000/login/?type=vet&mode=register"


class VetAuthForm(ctk.CTkFrame):
    def __init__(self, master, on_login_success=None, **kwargs):
        # NÃO repassa on_login_success para o CTkFrame
        super().__init__(master, fg_color="white", **kwargs)

        self.master = master
        self.on_login_success = on_login_success  # guarda a função de sucesso
        self._criar_tela_login()

    def _criar_tela_login(self):
        # Título grande
        ctk.CTkLabel(
            self,
            text="Acesse sua conta",
            font=("Arial", 24, "bold"),
            text_color="#1F2937"
        ).pack(anchor="w", padx=50, pady=(40, 5))

        # Frase menor abaixo do título
        ctk.CTkLabel(
            self,
            text="Digite seu email e senha para entrar",
            font=("Arial", 13),
            text_color="#6B7280"
        ).pack(anchor="w", padx=50, pady=(0, 30))

        # -----------------------
        # CAMPO DO EMAIL
        # -----------------------
        ctk.CTkLabel(self, text="Email", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(0, 5))

        self.email = ctk.CTkEntry(
            self,
            placeholder_text="digite seu email aqui",
            width=340,
            height=42,
            corner_radius=10
        )
        self.email.pack(fill="x", padx=50, pady=(0, 15))

        # -----------------------
        # CAMPO DA SENHA
        # -----------------------
        ctk.CTkLabel(self, text="Senha", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(0, 5))

        self.senha = ctk.CTkEntry(
            self,
            placeholder_text="••••••••",
            show="•",
            width=340,
            height=42,
            corner_radius=10
        )
        self.senha.pack(fill="x", padx=50, pady=(0, 25))

        # -----------------------
        # BOTÃO ENTRAR
        # -----------------------
        ctk.CTkButton(
            self,
            text="Entrar",
            width=340,
            height=45,
            fg_color=colors.BRAND_DARK_TEAL,
            hover_color="#0c5c54",
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.tentar_entrar
        ).pack(pady=(10, 20))

        # -----------------------
        # Link "Não tem conta?"
        # -----------------------
        link_frame = ctk.CTkFrame(self, fg_color="transparent")
        link_frame.pack(pady=10)

        ctk.CTkLabel(link_frame, text="Não tem conta ainda? ", text_color="gray").pack(side="left")

        link = ctk.CTkLabel(
            link_frame,
            text="Criar conta",
            text_color=colors.BRAND_DARK_TEAL,
            cursor="hand2",
            font=("Arial", 13, "underline")
        )
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: webbrowser.open(CADASTRO_URL))

    def tentar_entrar(self):
        """Aqui acontece a verificação quando clica em Entrar"""

        email_digitado = self.email.get().strip()
        senha_digitada = self.senha.get().strip()

        if email_digitado == "":
            Modal(self, "Atenção", "Digite seu email, por favor.", type="error")
            self.email.focus()
            return

        if senha_digitada == "":
            Modal(self, "Atenção", "Digite sua senha, por favor.", type="error")
            self.senha.focus()
            return

        if len(senha_digitada) < 6:
            Modal(self, "Atenção", "A senha precisa ter pelo menos 6 caracteres.", type="error")
            self.senha.focus()
            return

        # LOGIN DE TESTE
        if email_digitado == "teste@exemplo.com" and senha_digitada == "123456":
            Modal(self, "Sucesso", "Login realizado!\nBem-vindo(a) de volta!", type="success")

            # 🔥 chama a função que veio da LoginView (abre o dashboard)
            if self.on_login_success:
                self.after(1500, self.on_login_success)

        else:
            Modal(self, "Erro", "Email ou senha incorretos.\nTente novamente.", type="error")
