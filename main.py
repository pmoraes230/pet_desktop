import customtkinter as ctk
from app.views.login_view import LoginView
from app.widgets.dashboard_veterinario import DashboardVeterinario

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Veterinário")
        
        # Abre a janela maximizada (tamanho do monitor)
        self.after(0, lambda: self.state('zoomed')) 

        self.mostrar_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        LoginView(self, on_login_success=self.mostrar_dashboard)

    def mostrar_dashboard(self, tipo_usuario="admin"):
        self.limpar_tela()
        # O pack fill="both" e expand=True garante que o dashboard preencha a tela toda
        app_dash = DashboardVeterinario(self)
        app_dash.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()