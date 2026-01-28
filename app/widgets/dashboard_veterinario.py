import customtkinter as ctk


class DashboardVeterinario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # 👇 DEFINE TAMANHO DAS COLUNAS
        self.grid_columnconfigure(0, minsize=260)  # sidebar mais largo
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, fg_color="#14B8A6")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar,
            text="Menu",
            font=("Arial", 22),
            text_color="white"
        ).pack(pady=30)

        # ÁREA DE CONTEÚDO
        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)


        # Botões do menu
        self.criar_botao("Dashboard", self.tela_dashboard)
        self.criar_botao("Mensagens", self.tela_mensagens)
        self.criar_botao("Pacientes", self.tela_pacientes)
        self.criar_botao("Agenda", self.tela_agenda)
        self.criar_botao("Prontuários", self.tela_prontuarios)
        self.criar_botao("Financeiro", self.tela_financeiro)

        self.tela_dashboard()

    # =============================
    # Função para trocar telas
    # =============================
    def trocar_tela(self, func):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.after(50, func)

    def criar_botao(self, texto, comando):
        ctk.CTkButton(
            self.sidebar,
            text=texto,
            fg_color="#14B8A6",
            hover_color="188C7F",
            text_color="white",
            font=("Arial", 16),
            height=45,
            command=lambda: self.trocar_tela(comando)
        ).pack(fill="x", padx=20, pady=6)

    # =============================
    # TELAS
    # =============================
    def tela_dashboard(self):
        ctk.CTkLabel(
            self.content,
            text="Dashboard",
            font=("Arial", 32, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)

    def tela_mensagens(self):
        ctk.CTkLabel(
            self.content,
            text="Mensagens",
            font=("Arial", 26, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)

    def tela_pacientes(self):
        ctk.CTkLabel(
            self.content,
            text="Pacientes",
            font=("Arial", 26, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)

    def tela_agenda(self):
        ctk.CTkLabel(
            self.content,
            text="Agenda",
            font=("Arial", 26, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)

    def tela_prontuarios(self):
        ctk.CTkLabel(
            self.content,
            text="Prontuários",
            font=("Arial", 26, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)

    def tela_financeiro(self):
        ctk.CTkLabel(
            self.content,
            text="Financeiro",
            font=("Arial", 26, "bold"),
            text_color="#1f6aa5"
        ).pack(pady=20)
