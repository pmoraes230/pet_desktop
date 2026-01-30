# screens/financeiro_screen.py
import customtkinter as ctk


def create_financeiro_screen(master):
    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=20)

    ctk.CTkLabel(scroll, text="Painel Financeiro", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 25))

    metrics = ctk.CTkFrame(scroll, fg_color="transparent")
    metrics.pack(fill="x", pady=(0, 30))
    metrics.columnconfigure((0, 1, 2), weight=1)

    master.master.criar_card_fin_topo(metrics, "Entrada (Mês)", "R$ 14.500", 0)
    master.master.criar_card_fin_topo(metrics, "Saídas (Mês)", "R$ 5.230", 1)
    master.master.criar_card_fin_topo(metrics, "Saldo Líquido", "R$ 9.230", 2)

    main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
    main_grid.pack(fill="both", expand=True)
    main_grid.columnconfigure(0, weight=2)
    main_grid.columnconfigure(1, weight=1)

    chart = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0", height=300)
    chart.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
    ctk.CTkLabel(chart, text="Fluxo de Caixa Semestral", font=("Arial", 18, "bold")).pack(pady=15)

    trans = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
    trans.grid(row=0, column=1, sticky="nsew")
    ctk.CTkLabel(trans, text="Transações Recentes", font=("Arial", 18, "bold")).pack(pady=15)

    for _ in range(3):
        master.master.criar_item_transacao(trans, "Pagamento: Paçoca", "Hoje, 14:30", "+ R$ 150,00")