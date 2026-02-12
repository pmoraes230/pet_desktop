import customtkinter as ctk
import os
import sys
import tkinter as tk  # para PhotoImage
from app.views.login_view import LoginView
from app.views.dashboard_veterinario import DashboardVeterinario
from app.utils.loading_overlay import LoadingOverlay
from app.config.database import connectdb
from app.core.theme import apply_theme

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_theme()
        self.title("Coração em patas")

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            BASE_DIR = sys._MEIPASS
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        possible_paths = [
            os.path.join(BASE_DIR, "assets", "pet.ico"),
            os.path.join(BASE_DIR, "app", "assets", "pet.ico"),
            os.path.join(os.path.dirname(BASE_DIR), "assets", "pet.ico"),
            os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "assets", "pet.ico"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "assets", "pet.ico"),
        ]

        ICON_PATH = None
        for path in possible_paths:
            if os.path.exists(path):
                ICON_PATH = path
                break

        if ICON_PATH is None:
            print("Nenhum caminho válido para pet.ico encontrado")
            # Aqui você pode definir um fallback ou continuar sem ícone
        else:
            self.after(400, lambda: self.iconbitmap(ICON_PATH))

        # Maximizar janela
        self.after(100, self.maximizar_janela)

        # Loading overlay
        LoadingOverlay.get_instance(self)

        self.mostrar_login()

    def maximizar_janela(self):
        try:
            self.state('zoomed')
        except:
            self.attributes('-fullscreen', True)

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        LoginView(self, on_login_success=lambda user_data: self.mostrar_dashboard(user_data))

    def mostrar_dashboard(self, user_data=None):
        self.limpar_tela()
        app_dash = DashboardVeterinario(self, current_user=user_data, on_logout=self.mostrar_login)
        app_dash.pack(fill="both", expand=True)


if __name__ == "__main__":
    try:
        conn = connectdb()
        if conn:
            print("Conexão com o banco de dados estabelecida com sucesso.")
            conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

    app = App()
    app.mainloop()