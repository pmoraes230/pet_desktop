import customtkinter as ctk
from threading import Thread

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

        # ─── Configuração da janelinha pequena ───────────────────────────────
        WIDTH = 280
        HEIGHT = 140

        # Frame principal (fundo semi-transparente ou sólido)
        self.overlay = ctk.CTkFrame(
            self.master,
            fg_color="#000000",           # fundo escuro
            corner_radius=16,
            border_width=0
        )
        self.overlay.configure(width=WIDTH, height=HEIGHT)
        self.overlay.place(relx=0.5, rely=0.5, anchor="center")

        # Container interno para conteúdo
        inner = ctk.CTkFrame(self.overlay, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=20, pady=20)

        # Spinner
        self.spinner = ctk.CTkLabel(
            inner,
            text="⠋",
            font=("Arial", 36, "bold"),
            text_color="#14B8A6"          # cor do seu tema, ajuste se quiser
        )
        self.spinner.pack(pady=(0, 10))

        # Mensagem
        self.label = ctk.CTkLabel(
            inner,
            text=message,
            font=("Arial", 14),
            text_color="white"
        )
        self.label.pack()

        self._animate()

    def _animate(self):
        if not self.is_active or not self.spinner:
            return

        current = self.spinner.cget("text")
        spins = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        next_idx = (spins.index(current) + 1) % len(spins) if current in spins else 0
        self.spinner.configure(text=spins[next_idx])

        self.master.after(100, self._animate)   # mais fluido (10 fps)

    def hide(self):
        if not self.is_active:
            return
        self.is_active = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        self.spinner = None
        self.label = None

    def run_with_loading(self, func, message="Processando...", *args, **kwargs):
        self.show(message)

        def target():
            try:
                result = func(*args, **kwargs)
                self.master.after(0, self.hide)
                return result
            except Exception as e:
                self.master.after(0, self.hide)
                raise e

        thread = Thread(target=target, daemon=True)
        thread.start()


# Helpers (mantidos iguais)
def show_loading(message="Carregando..."):
    try:
        loading = LoadingOverlay.get_instance()
        loading.show(message)
    except RuntimeError as e:
        print("Erro ao mostrar loading:", e)


def hide_loading():
    try:
        loading = LoadingOverlay.get_instance()
        loading.hide()
    except RuntimeError:
        pass


def run_with_loading(func, message="Processando...", *args, **kwargs):
    try:
        loading = LoadingOverlay.get_instance()
        return loading.run_with_loading(func, message, *args, **kwargs)
    except RuntimeError as e:
        print("Erro ao executar com loading:", e)
        return func(*args, **kwargs)