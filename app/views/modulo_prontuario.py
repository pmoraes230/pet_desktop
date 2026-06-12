import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# Definição de Cores - Extraídas da segunda imagem de referência
class Colors:
    PRIMARY_DARK = "#004D40"      # Sidebar
    BG_LIGHT_GRAY = "#F8FAFC"     # Fundo geral
    CARD_BG = "#FFFFFF"           # Fundo dos cards
    BORDER_COLOR = "#E2E8F0"      # Cor das bordas
    
    TEXT_DARK = "#1E293B"         # Títulos
    TEXT_SECONDARY = "#64748B"    # Subtítulos e labels
    PLACEHOLDER_TEXT = "#94A3B8"
    
    ACCENT_PURPLE = "#A855F7"     # Botão Salvar e Evolução
    ACCENT_PURPLE_HOVER = "#9333EA"
    
    ACCENT_TEAL = "#2DD4BF"       # Ícone de Adicionar (+)
    ACCENT_CYAN = "#00838F"       # Ícone Medicamentos recentes
    
    INPUT_BG = "#F8FAFC"

colors = Colors()

class ModuloProntuario:
    def __init__(self, content_frame, prontuario_controller):
        self.content = content_frame
        self.controller = prontuario_controller
        self.pets_map = {}
        self.placeholder = (
            "Descreva aqui os sintomas, temperatura, peso, exame físico, diagnóstico, conduta "
            "clínica e procedimentos realizados..."
        )
        self.entry_med_nome = [] 
        self.entry_med_dosagem = []
        self.entry_med_frequencia = []
        self.med_frames = []

    def tela_prontuario(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.content.configure(fg_color=colors.BG_LIGHT_GRAY) 

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- HEADER ---
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título e Seletor
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_container,
            text="Prontuário eletrônico",
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w")

        paciente_row = ctk.CTkFrame(title_container, fg_color="transparent")
        paciente_row.pack(anchor="w", pady=(5, 0))

        ctk.CTkLabel(
            paciente_row,
            text="PACIENTE:",
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.PLACEHOLDER_TEXT
        ).pack(side="left", padx=(0, 10))

        self.combo_paciente = ctk.CTkOptionMenu(
            paciente_row,
            values=["Selecione um paciente..."],
            command=self.on_pet_selecionado,
            fg_color=colors.CARD_BG,
            button_color=colors.CARD_BG,
            button_hover_color=colors.INPUT_BG,
            text_color="#06B6D4", # Azul claro do texto no combo
            dropdown_fg_color=colors.CARD_BG,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            corner_radius=15,
            width=220,
            height=32
        )
        self.combo_paciente.pack(side="left")

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            header_frame,
            text="💾  Salvar prontuário",
            fg_color=colors.ACCENT_PURPLE,
            hover_color=colors.ACCENT_PURPLE_HOVER,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            width=180,
            height=45,
            corner_radius=22,
            command=self.salvar_prontuario
        )
        self.btn_salvar.pack(side="right", anchor="n")

        # --- CORPO ---
        main_grid = ctk.CTkFrame(container, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.grid_columnconfigure(0, weight=2)
        main_grid.grid_columnconfigure(1, weight=1)

        # --- COLUNA ESQUERDA ---
        left_col = ctk.CTkFrame(main_grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Evolução Clínica
        evol_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        evol_card.pack(fill="both", expand=True, pady=(0, 20))
        
        evol_head = ctk.CTkFrame(evol_card, fg_color="transparent")
        evol_head.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(evol_head, text="✎ Evolução Clínica", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.ACCENT_PURPLE).pack(side="left")
        ctk.CTkLabel(evol_head, text="Pressione Salvar após as anotações", font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(side="right")

        self.txt = ctk.CTkTextbox(evol_card, fg_color="transparent", text_color=colors.TEXT_SECONDARY, font=("Helvetica", 14), border_width=0)
        self.txt.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.txt.insert("1.0", self.placeholder)
        self.txt.bind("<FocusIn>", self._on_txt_focus_in)
        self.txt.bind("<FocusOut>", self._on_txt_focus_out)

        # Anexar Arquivo
        anexo_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        anexo_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(anexo_card, text="Anexar arquivo (Imagem ou PDF)", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 10))
        
        file_row = ctk.CTkFrame(anexo_card, fg_color="transparent")
        file_row.pack(fill="x", padx=20, pady=(0, 5))
        
        self.btn_file = ctk.CTkButton(file_row, text="Escolher arquivo", fg_color=colors.CARD_BG, text_color=colors.TEXT_DARK, border_width=1, border_color=colors.BORDER_COLOR, hover_color=colors.INPUT_BG, height=35, command=self._escolher_arquivo)
        self.btn_file.pack(side="left")
        
        self.lbl_file = ctk.CTkLabel(file_row, text="Nenhum arquivo escolhido", text_color=colors.PLACEHOLDER_TEXT, font=("Helvetica", 12))
        self.lbl_file.pack(side="left", padx=15)
        
        ctk.CTkLabel(anexo_card, text="Formatos permitidos: JPG, PNG e PDF", font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(anchor="w", padx=20, pady=(0, 15))

        # Adicionar Prescrição
        presc_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        presc_card.pack(fill="x")
        
        presc_head = ctk.CTkFrame(presc_card, fg_color="transparent")
        presc_head.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(presc_head, text="⊕ Adicionar Prescrição", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.TEXT_DARK).pack(side="left")
        
        # Labels das colunas (Igual imagem 2)
        labels_frame = ctk.CTkFrame(presc_card, fg_color="transparent")
        labels_frame.pack(fill="x", padx=20)
        labels_frame.grid_columnconfigure((0,1,2), weight=1)
        
        for i, text in enumerate(["Medicamento", "Dosagem", "Frequência"]):
            ctk.CTkLabel(labels_frame, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=colors.TEXT_DARK).grid(row=0, column=i, sticky="w")

        self.med_container = ctk.CTkFrame(presc_card, fg_color="transparent")
        self.med_container.pack(fill="x", padx=20, pady=5)
        
        self.adicionar_campo_medicamento() # Adiciona a primeira linha

        ctk.CTkLabel(presc_card, text="Deixe os campos em branco se não for prescrever medicamento agora.", font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(anchor="w", padx=20, pady=(5, 15))

        # --- COLUNA DIREITA ---
        right_col = ctk.CTkFrame(main_grid, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        # Histórico
        hist_card = ctk.CTkFrame(right_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        hist_card.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(hist_card, text="Histórico Clínico", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=20, pady=15)
        
        self.hist_scroll = ctk.CTkScrollableFrame(hist_card, fg_color="transparent")
        self.hist_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._mostrar_estado_vazio_historico()

        # Medicamentos Recentes
        med_rec_card = ctk.CTkFrame(right_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        med_rec_card.pack(fill="x")
        
        ctk.CTkLabel(med_rec_card, text="🔗 Medicamentos recentes", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.ACCENT_CYAN).pack(anchor="w", padx=20, pady=15)
        
        self.med_rec_list = ctk.CTkFrame(med_rec_card, fg_color="transparent")
        self.med_rec_list.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(self.med_rec_list, text="Nenhum medicamento prescrito\nrecentemente", font=("Helvetica", 11, "italic"), text_color=colors.PLACEHOLDER_TEXT).pack()

        self.carregar_pets()

    def adicionar_campo_medicamento(self):
        row_frame = ctk.CTkFrame(self.med_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure((0,1,2), weight=1)

        config = {"height": 38, "corner_radius": 8, "border_width": 1, "fg_color": colors.INPUT_BG, "border_color": colors.BORDER_COLOR}
        
        e_nome = ctk.CTkEntry(row_frame, placeholder_text="Ex: Amoxicilina 500mg", **config)
        e_nome.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        e_dose = ctk.CTkEntry(row_frame, placeholder_text="Ex: 1 comprimido", **config)
        e_dose.grid(row=0, column=1, padx=5, sticky="ew")
        
        e_freq = ctk.CTkEntry(row_frame, placeholder_text="Ex: 12/12h por 7 dias", **config)
        e_freq.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        self.entry_med_nome.append(e_nome)
        self.entry_med_dosagem.append(e_dose)
        self.entry_med_frequencia.append(e_freq)

    def _mostrar_estado_vazio_historico(self):
        empty_box = ctk.CTkFrame(self.hist_scroll, fg_color="transparent")
        empty_box.pack(expand=True, pady=50)
        
        ctk.CTkLabel(empty_box, text="📁", font=("Arial", 40), text_color=colors.BORDER_COLOR).pack()
        ctk.CTkLabel(empty_box, text="Nenhum registro anterior encontrado\npara este pet.", 
                     text_color=colors.PLACEHOLDER_TEXT, font=("Helvetica", 11), justify="center").pack(pady=10)

    # Métodos de suporte (mantendo lógica original com ajustes visuais)
    def carregar_pets(self):
        pets = self.controller.listar_pets()
        nomes = [p.get('NOME', 'Sem nome') for p in pets]
        for p in pets: self.pets_map[p.get('NOME')] = p.get('id')
        if nomes: self.combo_paciente.configure(values=["Selecione um paciente..."] + nomes)

    def on_pet_selecionado(self, nome):
        # Lógica de atualização de histórico aqui (conforme seu controller)
        pass

    def _escolher_arquivo(self):
        path = filedialog.askopenfilename()
        if path: self.lbl_file.configure(text=path.split("/")[-1])

    def _on_txt_focus_in(self, e):
        if self.txt.get("1.0", "end-1c") == self.placeholder:
            self.txt.delete("1.0", "end")
            self.txt.configure(text_color=colors.TEXT_DARK)

    def _on_txt_focus_out(self, e):
        if not self.txt.get("1.0", "end-1c").strip():
            self.txt.insert("1.0", self.placeholder)
            self.txt.configure(text_color=colors.PLACEHOLDER_TEXT)

    def salvar_prontuario(self):
        # Implementar chamada ao controller aqui
        messagebox.showinfo("Sucesso", "Prontuário salvo com sucesso!")