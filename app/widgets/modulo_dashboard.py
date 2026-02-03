import customtkinter as ctk

class ModuloDashboard:
    def tela_dashboard(self):
        # 1. Limpa o conteúdo anterior
        for widget in self.content.winfo_children():
            widget.destroy()

        # 2. Scrollable Frame (fg_color="transparent" para usar o fundo do content)
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        
        # 3. Configuração de colunas única para TODO o dashboard (3 colunas iguais)
        scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # --- LINHA 0: MÉTRICAS ---
        # Certifique-se de que o método criar_card_metrica use text_color="black" internamente
        self.criar_card_metrica(scroll, "1,240", "Total Pacientes", "🟦", "+12%", 0)
        self.criar_card_metrica(scroll, "8", "Consultas hoje", "🟩", None, 1)
        self.criar_card_metrica(scroll, "4.2K", "Faturamento mês", "🟨", None, 2)

        # --- LINHA 1: TÍTULOS (Com letras pretas) ---
        ctk.CTkLabel(scroll, text="Histórico Recente", font=("Arial", 18, "bold"), text_color="black").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(30, 15), padx=10
        )
        ctk.CTkLabel(scroll, text="Alertas de saúde", font=("Arial", 18, "bold"), text_color="black").grid(
            row=1, column=2, sticky="w", pady=(30, 15), padx=10
        )

        # --- LINHA 2: CARDS DE CONTEÚDO ---
        
        # Card de Histórico (Ocupa as colunas 0 e 1)
        hist_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        hist_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10)
        
        self.criar_linha_agendamento(hist_card, "09:00 AM", "Paçoca", "Vacinação Anual", "Confirmado", "#DCFCE7", "#166534")
        self.criar_linha_agendamento(hist_card, "10:30 AM", "Luna", "Avaliação", "Aguardando", "#FEF9C3", "#854D0E")

        # Card de Alertas (Ocupa a coluna 2 - exatamente embaixo do Faturamento)
        al_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        al_card.grid(row=2, column=2, sticky="nsew", padx=10)
        
        self.criar_item_alerta(al_card, "Bob (Golden)", "Queda brusca de peso registrada.")