# screens/config_perfil_screen.py
import customtkinter as ctk


def create_config_perfil_screen(master):
    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=40, pady=20)
    
    ctk.CTkLabel(scroll, text="Editar Perfil Profissional", font=("Arial", 24, "bold"), text_color="#1E293B").pack(pady=(0, 30))

    foto_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
    foto_card.pack(fill="x", pady=(0, 20))

    foto_cont = ctk.CTkFrame(foto_card, fg_color="transparent")
    foto_cont.pack(pady=30)

    av = ctk.CTkFrame(foto_cont, width=120, height=120, corner_radius=60, fg_color="#F1F5F9", border_width=4, border_color="#14B8A6")
    av.pack()
    av.pack_propagate(False)
    ctk.CTkLabel(av, text="U", font=("Arial", 40, "bold"), text_color="#14B8A6").place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkButton(foto_cont, text="📷", width=35, height=35, corner_radius=17, fg_color="#14B8A6").place(relx=0.9, rely=0.9, anchor="center")

    dados = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
    dados.pack(fill="x", pady=(0, 30))

    ctk.CTkLabel(dados, text="👤  Dados Pessoais", font=("Arial", 16, "bold")).pack(anchor="w", padx=30, pady=20)

    grid = ctk.CTkFrame(dados, fg_color="transparent")
    grid.pack(fill="x", padx=30, pady=(0, 20))
    grid.columnconfigure((0, 1), weight=1)

    master.master.criar_campo_input(grid, "NOME COMPLETO", "Usuário Exemplo", 0, 0)
    master.master.criar_campo_input(grid, "E-MAIL", "usuario@email.com", 0, 1)
    master.master.criar_campo_input(grid, "CRMV", "12345-SP", 1, 0)
    master.master.criar_campo_input(grid, "ESTADO (UF)", "São Paulo", 1, 1)