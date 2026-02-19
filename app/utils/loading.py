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
        if self.is_active: return
        self.is_active = True
        
        # Frame centralizado
        self.overlay = ctk.CTkFrame(self.master, fg_color="#000000", corner_radius=16)
        self.overlay.place(relx=0.5, rely=0.5, anchor="center", width=280, height=140)

        inner = ctk.CTkFrame(self.overlay, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=20, pady=20)

        self.spinner = ctk.CTkLabel(inner, text="⠋", font=("Arial", 36, "bold"), text_color="#14B8A6")
        self.spinner.pack(pady=(0, 10))

        self.label = ctk.CTkLabel(inner, text=message, font=("Arial", 14), text_color="white")
        self.label.pack()
        self._animate()

    def _animate(self):
        if not self.is_active or not self.spinner: return
        spins = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        current = self.spinner.cget("text")
        next_idx = (spins.index(current) + 1) % len(spins) if current in spins else 0
        self.spinner.configure(text=spins[next_idx])
        self.master.after(100, self._animate)

    def hide(self):
        if not self.is_active: return
        self.is_active = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def run_with_loading(self, func, message="Processando...", *args, **kwargs):
        self.show(message)
        def target():
            try:
                func(*args, **kwargs)
            finally:
                self.master.after(0, self.hide)
        Thread(target=target, daemon=True).start()

def run_with_loading(func, message="Processando...", *args, **kwargs):
    LoadingOverlay.get_instance().run_with_loading(func, message, *args, **kwargs)