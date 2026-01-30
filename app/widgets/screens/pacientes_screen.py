# screens/pacientes_screen.py
import customtkinter as ctk


def create_pacientes_screen(master):
    for widget in master.winfo_children():
        widget.destroy()

    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=20)

    header = ctk.CTkFrame(scroll, fg_color="transparent")
    header.pack(fill="x", pady=(0, 20))

    ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold")).pack(side="left")

    ctk.CTkButton(
        header,
        text="+ Novo Paciente",
        fg_color="#14B8A6",
        hover_color="#0D9488",
        width=150,
        corner_radius=10,
        # Importante: aponta para o método da classe principal
        command=master.master.abrir_popup_novo_paciente   # master → content → DashboardVeterinario
    ).pack(side="right")

    search_row = ctk.CTkFrame(scroll, fg_color="transparent")
    search_row.pack(fill="x", pady=(0, 30))

    ctk.CTkEntry(search_row, placeholder_text="🔍 Pesquise por tutor ou pet", height=45, corner_radius=22).pack(
        side="left", fill="x", expand=True, padx=(0, 15)
    )

    grid = ctk.CTkFrame(scroll, fg_color="transparent")
    grid.pack(fill="both", expand=True)
    grid.columnconfigure((0, 1, 2), weight=1)

    # Exemplo – você precisa passar o método criar_card_paciente ou reescrevê-lo
    # Opção 1: mover criar_card_paciente para cá (duplicação)
    # Opção 2: passar como argumento ou importar de um módulo components/
    # Por enquanto mantemos simples:
    master.master.criar_card_paciente(grid, "Paçoca", "Saudável", "Vira-lata • 4 Anos", "🐶", 0)
    master.master.criar_card_paciente(grid, "Luna", "Saudável", "Siamês • 2 Anos", "🐱", 1)
    master.master.criar_card_paciente(grid, "Thor", "Saudável", "Bulldog • 3 Anos", "🐶", 2)