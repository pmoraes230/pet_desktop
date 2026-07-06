import customtkinter as ctk
from app.core.i18n import tr
from app.core.theme import is_dark_mode


class Colors:
    PRIMARY = "#A855F7"
    SUCCESS = "#22C55E"
    DANGER = "#EF4444"

    def __init__(self):
        self.apply_appearance()

    def apply_appearance(self):
        if is_dark_mode():
            self.BG = "#111827"
            self.CARD_BG = "#1F2937"
            self.BORDER = "#374151"
            self.TEXT = "#F9FAFB"
            self.TEXT_MUTED = "#9CA3AF"
            return

        self.BG = "#F8FAFC"
        self.CARD_BG = "#FFFFFF"
        self.BORDER = "#E2E8F0"
        self.TEXT = "#1E293B"
        self.TEXT_MUTED = "#64748B"


colors = Colors()

class ModuloFinanceiro:
    def __init__(self, content_frame):
        self.content = content_frame

    def tela_financeiro(self):
        colors.apply_appearance()
        self.content.configure(fg_color=colors.BG)

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
            text=tr("Painel Financeiro"),
            font=("Arial", 24, "bold"),
            text_color=colors.TEXT
        ).pack(anchor="w", pady=(0, 25))

        # Cards de métricas no topo
        metrics = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 30))
        metrics.columnconfigure((0, 1, 2), weight=1)

        self.criar_card_fin_topo(metrics, tr("Entrada (Mês)"), "R$ 14.500", 0)
        self.criar_card_fin_topo(metrics, tr("Saídas (Mês)"), "R$ 5.230", 1)
        self.criar_card_fin_topo(metrics, tr("Saldo Líquido"), "R$ 9.230", 2)

        # Grid principal (gráfico + transações)
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=2)
        main_grid.columnconfigure(1, weight=1)
        main_grid.rowconfigure(0, weight=1)

        # Área do gráfico (placeholder por enquanto)
        chart = ctk.CTkFrame(
            main_grid,
            fg_color=colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=colors.BORDER
        )
        chart.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)

        # Placeholder simples para o gráfico (você pode substituir por matplotlib depois)
        ctk.CTkLabel(
            chart,
            text=tr("Gráfico de Entradas/Saídas (placeholder)"),
            font=("Arial", 16),
            text_color=colors.TEXT_MUTED
        ).pack(expand=True)

        # Transações recentes
        trans = ctk.CTkFrame(
            main_grid,
            fg_color=colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=colors.BORDER
        )
        trans.grid(row=0, column=1, sticky="nsew", pady=10)

        ctk.CTkLabel(
            trans,
            text=tr("Transações Recentes"),
            font=("Arial", 18, "bold"),
            text_color=colors.TEXT
        ).pack(pady=15, padx=15)

        # Exemplos de transações (depois virão do controller/banco)
        transacoes_exemplo = [
            (tr("Pagamento: Paçoca"), tr("Hoje, 14:30"), "+ R$ 150,00", "#22C55E"),
            (tr("Consulta: Luna"), tr("Ontem, 09:15"), "+ R$ 280,00", "#22C55E"),
            (tr("Compra de vacinas"), "05/02, 16:45", "- R$ 420,00", "#EF4444"),
        ]

        for tit, data, val, cor in transacoes_exemplo:
            self.criar_item_transacao(trans, tit, data, val, cor)

    def criar_card_fin_topo(self, master, titulo, valor, coluna):
        card = ctk.CTkFrame(
            master,
            fg_color=colors.CARD_BG,
            corner_radius=25,
            border_width=1,
            border_color=colors.BORDER
        )
        card.grid(row=0, column=coluna, padx=10, sticky="ew")

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color=colors.TEXT_MUTED,
            font=("Arial", 12, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 24, "bold"),
            text_color=colors.TEXT
        ).pack(pady=(0, 20))

    def criar_item_transacao(self, master, titulo, data, valor, cor="#22C55E"):
        item = ctk.CTkFrame(master, fg_color="transparent")
        item.pack(fill="x", padx=20, pady=8)

        info = ctk.CTkFrame(item, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info, text=titulo, font=("Arial", 13, "bold"), text_color=colors.TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text=data, font=("Arial", 11), text_color=colors.TEXT_MUTED).pack(anchor="w")

        ctk.CTkLabel(
            item,
            text=valor,
            text_color=cor,
            font=("Arial", 13, "bold")
        ).pack(side="right", padx=10)
