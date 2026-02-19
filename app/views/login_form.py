import customtkinter as ctk
import webbrowser
from threading import Thread
from app.views.modal import Modal
from app.controllers.auth_controller import AuthController
import app.core.colors as colors

# ============================================================
# 1. CLASSE DE CARREGAMENTO (LoadingOverlay) CORRIGIDA
# ============================================================
class LoadingOverlay:
    _instance = None

    @classmethod
    def get_instance(cls, master=None):
        if cls._instance is None:
            if master is None:
                raise RuntimeError("Primeira chamada precisa passar a janela root (master)")
            cls._instance = cls(master)
        return cls._instance

    def __init__(self, master):
        self.master = master
        self.overlay = None
        self.is_active = False

    def show(self, message="Processando..."):
        if self.is_active:
            return
        self.is_active = True
        
        WIDTH, HEIGHT = 280, 140

        # --- CORREÇÃO AQUI: width e height passados no CTkFrame ---
        self.overlay = ctk.CTkFrame(
            self.master, 
            width=WIDTH, 
            height=HEIGHT, 
            fg_color="#000000", 
            corner_radius=16, 
            border_width=0
        )
        # O place agora fica limpo, sem width/height
        self.overlay.place(relx=0.5, rely=0.5, anchor="center")
        
        inner = ctk.CTkFrame(self.overlay, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.spinner = ctk.CTkLabel(inner, text="⠋", font=("Arial", 36, "bold"), text_color="#14B8A6")
        self.spinner.pack(pady=(0, 10))
        
        self.label = ctk.CTkLabel(inner, text=message, font=("Arial", 14), text_color="white")
        self.label.pack()
        self._animate()

    def _animate(self):
        if not self.is_active or not self.spinner:
            return
        current = self.spinner.cget("text")
        spins = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        next_idx = (spins.index(current) + 1) % len(spins) if current in spins else 0
        self.spinner.configure(text=spins[next_idx])
        self.master.after(100, self._animate)

    def show_success(self, message="Sucesso!"):
        if not self.is_active:
            self.show(message)
        self.is_active = False 
        if self.spinner:
            self.spinner.configure(text="✔", text_color="#10B981") 
        if self.label:
            self.label.configure(text=message, text_color="white")
        self.master.after(1500, self.hide)

    def hide(self):
        if not self.is_active:
            return
        self.is_active = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def run_with_loading(self, func, message="Processando...", *args, **kwargs):
        self.show(message)
        def target():
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Erro: {e}")
                self.master.after(0, self.hide)
        Thread(target=target, daemon=True).start()

def run_with_loading(func, message="Processando...", *args, **kwargs):
    LoadingOverlay.get_instance().run_with_loading(func, message, *args, **kwargs)


# ============================================================
# 2. SEU FORMULÁRIO DE LOGIN (VetAuthForm)
# ============================================================
CADASTRO_URL = "http://127.0.0.1:8000/login/?type=vet&mode=register"

class VetAuthForm(ctk.CTkFrame):
    def __init__(self, master, on_login_success=None, **kwargs):
        super().__init__(master, fg_color="white", **kwargs)
        self.master = master
        self.on_login_success = on_login_success  
        
        # Inicializa o Singleton
        LoadingOverlay.get_instance(self.master.winfo_toplevel())
        
        self._criar_tela_login()

    def _criar_tela_login(self):
        ctk.CTkLabel(self, text="Acesse sua conta", font=("Arial", 24, "bold"), text_color="#1F2937").pack(anchor="w", padx=50, pady=(40, 5))
        ctk.CTkLabel(self, text="Digite seu email e senha para entrar", font=("Arial", 13), text_color="#6B7280").pack(anchor="w", padx=50, pady=(0, 30))
        
        ctk.CTkLabel(self, text="Email", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(0, 5))
        self.email = ctk.CTkEntry(self, placeholder_text="digite seu email aqui", width=340, height=42, corner_radius=10)
        self.email.pack(fill="x", padx=50, pady=(0, 15))

        ctk.CTkLabel(self, text="Senha", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(0, 5))
        self.senha = ctk.CTkEntry(self, placeholder_text="••••••••", show="•", width=340, height=42, corner_radius=10)
        self.senha.pack(fill="x", padx=50, pady=(0, 25))
        
        self.email.bind("<Return>", lambda event: self.tentar_entrar())        
        self.senha.bind("<Return>", lambda event: self.tentar_entrar())

        ctk.CTkButton(
            self, text="Entrar", width=340, height=45, fg_color=colors.BRAND_DARK_TEAL,
            hover_color="#0c5c54", corner_radius=10, font=("Arial", 14, "bold"),
            command=self.tentar_entrar
        ).pack(pady=(10, 20))

        link_frame = ctk.CTkFrame(self, fg_color="transparent")
        link_frame.pack(pady=10)
        ctk.CTkLabel(link_frame, text="Não tem conta ainda? ", text_color="gray").pack(side="left")
        link = ctk.CTkLabel(link_frame, text="Criar conta", text_color=colors.BRAND_DARK_TEAL, cursor="hand2", font=("Arial", 13, "underline"))
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: webbrowser.open(CADASTRO_URL))
        self.email.focus()

    def tentar_entrar(self):
        email_digitado = self.email.get().strip()
        senha_digitada = self.senha.get().strip()

        if email_digitado == "" or senha_digitada == "":
            Modal(self, "Atenção", "Preencha todos os campos.", type="error")
            return

        run_with_loading(self._executar_login_com_loading, "Autenticando...", email_digitado, senha_digitada)

    def _executar_login_com_loading(self, email, senha):
        try:
            controller = AuthController(email, senha)
            sucesso, resposta = controller.login()
            
            if sucesso:
                self.after(0, lambda: self._login_sucesso(controller, resposta))
            else:
                self.after(0, lambda: LoadingOverlay.get_instance().hide())
                self.after(0, lambda: Modal(self, "Erro", resposta['message'], type="error"))
        except Exception as e:
            self.after(0, lambda: LoadingOverlay.get_instance().hide())
            self.after(0, lambda: Modal(self, "Erro", f"Erro crítico: {str(e)}", type="error"))

    def _login_sucesso(self, controller, resposta):
        self.user_data = controller.get_user_data()
        nome_usuario = self.user_data.get("name", "Usuário")
        loader = LoadingOverlay.get_instance()
        loader.show_success(f"Bem-vindo, {nome_usuario}!")
        if self.on_login_success:
            self.after(1600, lambda: self.on_login_success(self.user_data))