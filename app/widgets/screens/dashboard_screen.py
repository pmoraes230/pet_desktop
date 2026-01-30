# screens/dashboard_screen.py
import customtkinter as ctk


def create_dashboard_screen(master):
    for widget in master.winfo_children():
        widget.destroy()

    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=25, pady=25)
    
    scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

    # Métricas
    master.master.criar_card_metrica(scroll, "1,240", "Total Pacientes", "🟦", "+12%", 0)
    master.master.criar_card_metrica(scroll, "8", "Consultas hoje", "🟩", None, 1)
    master.master.criar_card_metrica(scroll, "4.2K", "Faturamento mês", "🟨", None, 2)

    # Títulos
    ctk.CTkLabel(scroll, text="Histórico Recente", font=("Arial", 18, "bold"), text_color="black").grid(
        row=1, column=0, columnspan=2, sticky="w", pady=(30, 15), padx=10
    )
    ctk.CTkLabel(scroll, text="Alertas de saúde", font=("Arial", 18, "bold"), text_color="black").grid(
        row=1, column=2, sticky="w", pady=(30, 15), padx=10
    )

    # Card Histórico
    hist_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
    hist_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10)
    
    master.master.criar_linha_agendamento(hist_card, "09:00 AM", "Paçoca", "Vacinação Anual", "Confirmado", "#DCFCE7", "#166534")
    master.master.criar_linha_agendamento(hist_card, "10:30 AM", "Luna", "Avaliação", "Aguardando", "#FEF9C3", "#854D0E")

    # Card Alertas
    al_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
    al_card.grid(row=2, column=2, sticky="nsew", padx=10)
    
    master.master.criar_item_alerta(al_card, "Bob (Golden)", "Queda brusca de peso registrada.")