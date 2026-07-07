from threading import Thread

import customtkinter as ctk
import tkinter as tk


def _safe_execute(master, callback, *args, **kwargs):
    if master is None or callback is None:
        return

    try:
        if not hasattr(master, "winfo_exists") or not master.winfo_exists():
            return
    except tk.TclError:
        return

    try:
        callback(*args, **kwargs)
    except (tk.TclError, RuntimeError):
        pass


class LoadingOverlay:
    _instances = {}

    @classmethod
    def get_instance(cls, master=None):
        if master is None:
            if not cls._instances:
                raise RuntimeError("Primeira chamada precisa passar a janela root (master)")
            return next(iter(cls._instances.values()))

        master = master.winfo_toplevel()
        key = str(master)
        if key not in cls._instances:
            cls._instances[key] = cls(master)
        return cls._instances[key]

    def __init__(self, master):
        self.master = master
        self.overlay = None
        self.spinner = None
        self.label = None
        self.is_active = False

    def show(self, message="Processando..."):
        if self.is_active:
            if self.label:
                self.label.configure(text=message)
            return

        self.is_active = True
        self.overlay = ctk.CTkFrame(
            self.master,
            width=300,
            height=150,
            fg_color="#1F2937",
            corner_radius=10,
        )
        self.overlay.place(relx=0.5, rely=0.5, anchor="center")
        self.overlay.pack_propagate(False)
        self.overlay.lift()

        inner = ctk.CTkFrame(self.overlay, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=20, pady=20)

        self.spinner = ctk.CTkLabel(
            inner,
            text="|",
            font=("Arial", 36, "bold"),
            text_color="#14B8A6",
        )
        self.spinner.pack(pady=(0, 10))

        self.label = ctk.CTkLabel(
            inner,
            text=message,
            font=("Arial", 14),
            text_color="white",
        )
        self.label.pack()

        self._animate()

    def _animate(self):
        if not self.is_active or not self.spinner:
            return

        spins = ["|", "/", "-", "\\"]
        current = self.spinner.cget("text")
        next_idx = (spins.index(current) + 1) % len(spins) if current in spins else 0
        self.spinner.configure(text=spins[next_idx])
        self.master.after(120, self._animate)

    def hide(self):
        self.is_active = False
        if self.overlay:
            try:
                if self.overlay.winfo_exists():
                    self.overlay.destroy()
            except tk.TclError:
                pass
            self.overlay = None
        self.spinner = None
        self.label = None

    def show_success(self, message="Sucesso!"):
        if not self.is_active:
            self.show(message)

        self.is_active = False
        if self.spinner:
            self.spinner.configure(text="OK", text_color="#10B981")
        if self.label:
            self.label.configure(text=message, text_color="white")
        self.master.after(1200, self.hide)

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


def run_backend_task(master, task, on_success=None, on_error=None, message="Processando..."):
    """Executa uma tarefa de backend sem travar a interface.

    A funcao task roda em uma thread. Os callbacks on_success e on_error rodam
    na thread principal do CustomTkinter, entao podem atualizar widgets.
    """
    loader = LoadingOverlay.get_instance(master)
    loader.show(message)

    def finish_success(result):
        loader.hide()
        _safe_execute(master, on_success, result)

    def finish_error(error):
        loader.hide()
        if on_error:
            _safe_execute(master, on_error, error)
        else:
            print(f"Erro em tarefa de backend: {error}")

    def target():
        try:
            result = task()
            master.after(0, lambda: finish_success(result))
        except Exception as error:
            master.after(0, lambda error=error: finish_error(error))

    Thread(target=target, daemon=True).start()
