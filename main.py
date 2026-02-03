import customtkinter as ctk
from app.views.login_view import LoginView
from app.widgets.dashboard_veterinario import DashboardVeterinario
from app.config.database import connectdb
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Coração em patas")
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ICON_PATH = os.path.join(BASE_DIR, "assets", "pet.ico")

        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)
        
        self.after(0, lambda: self.state('zoomed')) 
        self.mostrar_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        # on_login_success receberá user_data (dicionário com 'id', 'name', 'email')
        LoginView(self, on_login_success=lambda user_data: self.mostrar_dashboard(user_data))

    def mostrar_dashboard(self, user_data=None):
        self.limpar_tela()
        app_dash = DashboardVeterinario(self, current_user=user_data, on_logout=self.mostrar_login)
        app_dash.pack(fill="both", expand=True)

if __name__ == "__main__":
    if connectdb:
        print("Conexão com o banco de dados estabelecida com sucesso.")
    
    app = App()
    app.mainloop()