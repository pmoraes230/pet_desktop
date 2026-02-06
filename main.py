import customtkinter as ctk
import os
from app.views.login_view import LoginView
from app.views.dashboard_veterinario import DashboardVeterinario
from app.utils.loading_overlay import LoadingOverlay
from app.config.database import connectdb  
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Coração em patas")

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ICON_PATH = os.path.join(BASE_DIR, "assets", "pet.ico")

        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Não foi possível carregar o ícone: {e}")

        # Maximizar a janela de forma confiável no CustomTkinter
        self.after(100, self.maximizar_janela)  # pequeno delay evita sobrescrita

        # Inicializa o gerenciador de loading global (se você usa em outros lugares)
        LoadingOverlay.get_instance(self)

        self.mostrar_login()

    def maximizar_janela(self):
        """Maximiza a janela de forma cross-platform e confiável"""
        try:
            self.state('zoomed')           # Windows/Linux (maximizado)
        except:
            # Fallback: geometria full screen (funciona em mais plataformas)
            self.attributes('-fullscreen', True)
            # Ou use: self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        # on_login_success recebe user_data (dict com 'id', 'name', etc.)
        LoginView(self, on_login_success=lambda user_data: self.mostrar_dashboard(user_data))

    def mostrar_dashboard(self, user_data=None):
        self.limpar_tela()
        app_dash = DashboardVeterinario(self, current_user=user_data, on_logout=self.mostrar_login)
        app_dash.pack(fill="both", expand=True)


if __name__ == "__main__":
    # Testa a conexão com o banco de forma correta
    try:
        conn = connectdb()
        if conn:
            print("Conexão com o banco de dados estabelecida com sucesso.")
            conn.close() 
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

    app = App()
    app.mainloop()