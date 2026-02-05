import customtkinter as ctk

class ModuloFinanceiro:
    def __init__(self, content_frame):
        self.content = content_frame

    def tela_financeiro(self):
        # Limpa tudo que estava na área de conteúdo
        for widget in self.content.winfo_children():
            widget.destroy()

        # Cria o scroll principal
        scroll = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            orientation="vertical"
        )
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            scroll,
            text="Painel Financeiro",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", pady=(0, 25))

        # Cards de métricas no topo
        metrics = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 30))
        metrics.columnconfigure((0, 1, 2), weight=1)

        self.criar_card_fin_topo(metrics, "Entrada (Mês)", "R$ 14.500", 0)
        self.criar_card_fin_topo(metrics, "Saídas (Mês)", "R$ 5.230", 1)
        self.criar_card_fin_topo(metrics, "Saldo Líquido", "R$ 9.230", 2)

        # Grid principal (gráfico + transações)
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=2)
        main_grid.columnconfigure(1, weight=1)
        main_grid.rowconfigure(0, weight=1)

        # Área do gráfico (placeholder por enquanto)
        chart = ctk.CTkFrame(
            main_grid,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0"
        )
        chart.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)

        # Placeholder simples para o gráfico (você pode substituir por matplotlib depois)
        ctk.CTkLabel(
            chart,
            text="Gráfico de Entradas/Saídas (placeholder)",
            font=("Arial", 16),
            text_color="#64748B"
        ).pack(expand=True)

        # Transações recentes
        trans = ctk.CTkFrame(
            main_grid,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0"
        )
        trans.grid(row=0, column=1, sticky="nsew", pady=10)

        ctk.CTkLabel(
            trans,
            text="Transações Recentes",
            font=("Arial", 18, "bold")
        ).pack(pady=15, padx=15)

        # Exemplos de transações (depois virão do controller/banco)
        transacoes_exemplo = [
            ("Pagamento: Paçoca", "Hoje, 14:30", "+ R$ 150,00", "#22C55E"),
            ("Consulta: Luna", "Ontem, 09:15", "+ R$ 280,00", "#22C55E"),
            ("Compra de vacinas", "05/02, 16:45", "- R$ 420,00", "#EF4444"),
        ]

        for tit, data, val, cor in transacoes_exemplo:
            self.criar_item_transacao(trans, tit, data, val, cor)

    def criar_card_fin_topo(self, master, titulo, valor, coluna):
        card = ctk.CTkFrame(
            master,
            fg_color="white",
            corner_radius=25,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=0, column=coluna, padx=10, sticky="ew")

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color="#64748B",
            font=("Arial", 12, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 20))

    def criar_item_transacao(self, master, titulo, data, valor, cor="#22C55E"):
        item = ctk.CTkFrame(master, fg_color="transparent")
        item.pack(fill="x", padx=20, pady=8)

        info = ctk.CTkFrame(item, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info, text=titulo, font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=data, font=("Arial", 11), text_color="#64748B").pack(anchor="w")

        ctk.CTkLabel(
            item,
            text=valor,
            text_color=cor,
            font=("Arial", 13, "bold")
        ).pack(side="right", padx=10)