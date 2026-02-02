import customtkinter as ctk

class ModuloFinanceiro:
    def tela_financeiro(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        ctk.CTkLabel(scroll, text="Painel Financeiro", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 25))
        metrics = ctk.CTkFrame(scroll, fg_color="transparent"); metrics.pack(fill="x", pady=(0, 30)); metrics.columnconfigure((0, 1, 2), weight=1)
        self.criar_card_fin_topo(metrics, "Entrada (Mês)", "R$ 14.500", 0)
        self.criar_card_fin_topo(metrics, "Saídas (Mês)", "R$ 5.230", 1)
        self.criar_card_fin_topo(metrics, "Saldo Líquido", "R$ 9.230", 2)
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent"); main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=2); main_grid.columnconfigure(1, weight=1)
        chart = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0", height=300); chart.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        trans = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0"); trans.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(trans, text="Transações Recentes", font=("Arial", 18, "bold")).pack(pady=15)
        for _ in range(3): self.criar_item_transacao(trans, "Pagamento: Paçoca", "Hoje, 14:30", "+ R$ 150,00")

    def criar_card_fin_topo(self, master, tit, val, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0") 
        c.grid(row=0, column=col, padx=10, sticky="ew")
        ctk.CTkLabel(c, text=tit, text_color="#64748B", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(c, text=val, font=("Arial", 24, "bold")).pack(pady=(0, 20))

    def criar_item_transacao(self, master, tit, data, val):
        i = ctk.CTkFrame(master, fg_color="transparent"); i.pack(fill="x", padx=20, pady=10)
        t = ctk.CTkFrame(i, fg_color="transparent"); t.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t, text=tit, font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=data, font=("Arial", 11), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(i, text=val, text_color="#22C55E", font=("Arial", 13, "bold")).pack(side="right")