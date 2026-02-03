import customtkinter as ctk
from app.views.login_view import LoginView
from app.widgets.dashboard_veterinario import DashboardVeterinario
from app.config.database import connectdb

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Veterinário")
        self.after(0, lambda: self.state('zoomed')) 
        self.mostrar_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        LoginView(self, on_login_success=self.mostrar_dashboard)

    def mostrar_dashboard(self):
        self.limpar_tela()
        app_dash = DashboardVeterinario(self, on_logout=self.mostrar_login)
        app_dash.pack(fill="both", expand=True)

if __name__ == "__main__":
    if connectdb:
        print("Conexão com o banco de dados estabelecida com sucesso.")
    app = App()
    app.mainloop()