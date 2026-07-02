import customtkinter as ctk
from datetime import datetime
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
from PIL import Image
from app.services.s3_client import upload_prontuario_arquivo_s3, get_url_s3

from app.core.i18n import tr
from app.utils.loading import run_backend_task


class Colors:
    PRIMARY_DARK = "#004D40"
    BG_LIGHT_GRAY = "#F8FAFC"
    CARD_BG = "#FFFFFF"
    BORDER_COLOR = "#E2E8F0"
    TEXT_DARK = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    PLACEHOLDER_TEXT = "#94A3B8"
    ACCENT_PURPLE = "#A855F7"
    ACCENT_PURPLE_HOVER = "#9333EA"
    ACCENT_TEAL = "#2DD4BF"
    ACCENT_CYAN = "#00838F"
    INPUT_BG = "#F8FAFC"


colors = Colors()


class ModuloProntuario:
    def __init__(self, content_frame, prontuario_controller):
        self.content = content_frame
        self.controller = prontuario_controller
        self.pets_map = {}
        self.arquivo_path = None
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

        self.placeholder = tr(
            "Descreva aqui os sintomas, temperatura, peso, exame físico, diagnóstico, conduta clínica e procedimentos realizados..."
        )
        self.content.configure(fg_color=colors.BG_LIGHT_GRAY)

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_container,
            text=tr("Prontuário eletrônico"),
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=colors.TEXT_DARK,
        ).pack(anchor="w")

        paciente_row = ctk.CTkFrame(title_container, fg_color="transparent")
        paciente_row.pack(anchor="w", pady=(5, 0))

        ctk.CTkLabel(
            paciente_row,
            text=tr("PACIENTE:"),
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.PLACEHOLDER_TEXT,
        ).pack(side="left", padx=(0, 10))

        self.combo_paciente = ctk.CTkOptionMenu(
            paciente_row,
            values=[tr("Selecione um paciente...")],
            command=self.on_pet_selecionado,
            fg_color=colors.CARD_BG,
            button_color=colors.CARD_BG,
            button_hover_color=colors.INPUT_BG,
            text_color="#06B6D4",
            dropdown_fg_color=colors.CARD_BG,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            corner_radius=15,
            width=220,
            height=32,
        )
        self.combo_paciente.pack(side="left")

        ctk.CTkButton(
            header_frame,
            text=tr("💾  Salvar prontuário"),
            fg_color=colors.ACCENT_PURPLE,
            hover_color=colors.ACCENT_PURPLE_HOVER,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            width=180,
            height=45,
            corner_radius=22,
            command=self.salvar_prontuario,
        ).pack(side="right", anchor="n")

        main_grid = ctk.CTkFrame(container, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.grid_columnconfigure(0, weight=2)
        main_grid.grid_columnconfigure(1, weight=1)

        left_col = ctk.CTkFrame(main_grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        evol_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        evol_card.pack(fill="both", expand=True, pady=(0, 20))

        evol_head = ctk.CTkFrame(evol_card, fg_color="transparent")
        evol_head.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(evol_head, text=tr("✎ Evolução Clínica"), font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.ACCENT_PURPLE).pack(side="left")
        ctk.CTkLabel(evol_head, text=tr("Pressione Salvar após as anotações"), font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(side="right")

        self.txt = ctk.CTkTextbox(evol_card, fg_color="transparent", text_color=colors.TEXT_SECONDARY, font=("Helvetica", 14), border_width=0)
        self.txt.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.txt.insert("1.0", self.placeholder)
        self.txt.bind("<FocusIn>", self._on_txt_focus_in)
        self.txt.bind("<FocusOut>", self._on_txt_focus_out)

        anexo_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        anexo_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(anexo_card, text=tr("Anexar arquivo (Imagem ou PDF)"), font=ctk.CTkFont(size=14, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 10))

        file_row = ctk.CTkFrame(anexo_card, fg_color="transparent")
        file_row.pack(fill="x", padx=20, pady=(0, 5))
        self.btn_file = ctk.CTkButton(
            file_row,
            text=tr("Escolher arquivo"),
            fg_color=colors.CARD_BG,
            text_color=colors.TEXT_DARK,
            border_width=1,
            border_color=colors.BORDER_COLOR,
            hover_color=colors.INPUT_BG,
            height=35,
            command=self._escolher_arquivo,
        )
        self.btn_file.pack(side="left")
        self.lbl_file = ctk.CTkLabel(file_row, text=tr("Nenhum arquivo escolhido"), text_color=colors.PLACEHOLDER_TEXT, font=("Helvetica", 12))
        self.lbl_file.pack(side="left", padx=15)
        ctk.CTkLabel(anexo_card, text=tr("Formatos permitidos: JPG, PNG e PDF"), font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(anchor="w", padx=20, pady=(0, 15))

        presc_card = ctk.CTkFrame(left_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        presc_card.pack(fill="x")

        presc_head = ctk.CTkFrame(presc_card, fg_color="transparent")
        presc_head.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(presc_head, text=tr("⊕ Adicionar Prescrição"), font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.TEXT_DARK).pack(side="left")

        labels_frame = ctk.CTkFrame(presc_card, fg_color="transparent")
        labels_frame.pack(fill="x", padx=20)
        labels_frame.grid_columnconfigure((0, 1, 2), weight=1)
        for i, text in enumerate([tr("Medicamento"), tr("Dosagem"), tr("Frequência")]):
            ctk.CTkLabel(labels_frame, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=colors.TEXT_DARK).grid(row=0, column=i, sticky="w")

        self.med_container = ctk.CTkFrame(presc_card, fg_color="transparent")
        self.med_container.pack(fill="x", padx=20, pady=5)
        self.adicionar_campo_medicamento()

        ctk.CTkLabel(presc_card, text=tr("Deixe os campos em branco se não for prescrever medicamento agora."), font=ctk.CTkFont(size=10), text_color=colors.PLACEHOLDER_TEXT).pack(anchor="w", padx=20, pady=(5, 15))

        right_col = ctk.CTkFrame(main_grid, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        hist_card = ctk.CTkFrame(right_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        hist_card.pack(fill="both", expand=True, pady=(0, 20))
        ctk.CTkLabel(hist_card, text=tr("Histórico Clínico"), font=ctk.CTkFont(size=16, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=20, pady=15)

        self.hist_scroll = ctk.CTkScrollableFrame(hist_card, fg_color="transparent")
        self.hist_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._mostrar_estado_vazio_historico()

        med_rec_card = ctk.CTkFrame(right_col, fg_color=colors.CARD_BG, corner_radius=20, border_width=1, border_color=colors.BORDER_COLOR)
        med_rec_card.pack(fill="x")
        ctk.CTkLabel(med_rec_card, text=tr("🔗 Medicamentos recentes"), font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.ACCENT_CYAN).pack(anchor="w", padx=20, pady=15)

        self.med_rec_list = ctk.CTkFrame(med_rec_card, fg_color="transparent")
        self.med_rec_list.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(self.med_rec_list, text=tr("Nenhum medicamento prescrito\nrecentemente"), font=("Helvetica", 11, "italic"), text_color=colors.PLACEHOLDER_TEXT).pack()

        self.carregar_pets()

    def adicionar_campo_medicamento(self):
        row_frame = ctk.CTkFrame(self.med_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure((0, 1, 2), weight=1)

        config = {"height": 38, "corner_radius": 8, "border_width": 1, "fg_color": colors.INPUT_BG, "border_color": colors.BORDER_COLOR}

        e_nome = ctk.CTkEntry(row_frame, placeholder_text="Ex: Amoxicilina 500mg", **config)
        e_nome.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        e_dose = ctk.CTkEntry(row_frame, placeholder_text=tr("Ex: 1 comprimido"), **config)
        e_dose.grid(row=0, column=1, padx=5, sticky="ew")

        e_freq = ctk.CTkEntry(row_frame, placeholder_text=tr("Ex: 12/12h por 7 dias"), **config)
        e_freq.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        self.entry_med_nome.append(e_nome)
        self.entry_med_dosagem.append(e_dose)
        self.entry_med_frequencia.append(e_freq)

    def _mostrar_estado_vazio_historico(self):
        for widget in self.hist_scroll.winfo_children():
            widget.destroy()

        empty_box = ctk.CTkFrame(self.hist_scroll, fg_color="transparent")
        empty_box.pack(expand=True, pady=50)
        ctk.CTkLabel(empty_box, text="📁", font=("Arial", 40), text_color=colors.BORDER_COLOR).pack()
        ctk.CTkLabel(
            empty_box,
            text=tr("Nenhum registro anterior encontrado\npara este pet."),
            text_color=colors.PLACEHOLDER_TEXT,
            font=("Helvetica", 11),
            justify="center",
        ).pack(pady=10)

    def carregar_pets(self):
        run_backend_task(
            self.content,
            self.controller.listar_pets,
            on_success=self._finalizar_carregamento_pets,
            on_error=lambda erro: messagebox.showerror("Erro", f"Nao foi possivel carregar os pacientes: {erro}"),
            message="Carregando pacientes...",
        )

    def _finalizar_carregamento_pets(self, pets):
        nomes = [p.get("NOME", tr("Sem nome")) for p in pets]
        for p in pets:
            self.pets_map[p.get("NOME")] = p.get("id")
        if nomes:
            self.combo_paciente.configure(values=[tr("Selecione um paciente...")] + nomes)

    def on_pet_selecionado(self, nome):
        # Lógica de atualização de histórico aqui (conforme seu controller)
        pet_id = self.pets_map.get(nome)
        if not pet_id:
            self._mostrar_estado_vazio_historico()
            return

        run_backend_task(
            self.content,
            lambda: self.controller.historico(pet_id),
            on_success=self._renderizar_historico,
            on_error=lambda erro: messagebox.showerror("Erro", f"Nao foi possivel carregar o historico: {erro}"),
            message="Carregando historico...",
        )

    def _renderizar_historico(self, historico):
        for widget in self.hist_scroll.winfo_children():
            widget.destroy()

        if not historico:
            self._mostrar_estado_vazio_historico()
            return

        for registro in historico:
            self._criar_card_historico(registro)

    def _criar_card_historico(self, registro):
        card = ctk.CTkFrame(
            self.hist_scroll,
            fg_color=colors.INPUT_BG,
            corner_radius=12,
            border_width=1,
            border_color=colors.BORDER_COLOR
        )
        card.pack(fill="x", padx=5, pady=(0, 10))

        data = registro.get("DATA_CRIACAO")
        if isinstance(data, datetime):
            data_texto = data.strftime("%d/%m/%Y %H:%M")
        else:
            data_texto = str(data or "Data nao informada")

        ctk.CTkLabel(
            card,
            text=data_texto,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=colors.ACCENT_PURPLE
        ).pack(anchor="w", padx=12, pady=(10, 4))

        campos = [
            ("Historico", registro.get("HISTORICO_VETERINARIO")),
            ("Motivo", registro.get("MOTIVO_CONSULTA")),
            ("Avaliacao", registro.get("AVALIACAO_GERAL")),
            ("Procedimentos", registro.get("PROCEDIMENTOS")),
            ("Diagnostico", registro.get("DIAGNOSTICO_CONSLUSIVO")),
            ("Observacao", registro.get("OBSERVACAO")),
        ]

        for titulo, valor in campos:
            if valor and str(valor).strip():
                ctk.CTkLabel(
                    card,
                    text=f"{titulo}: {valor}",
                    font=ctk.CTkFont(size=12),
                    text_color=colors.TEXT_SECONDARY,
                    justify="left",
                    wraplength=280
                ).pack(anchor="w", padx=12, pady=2)

        arquivo = registro.get("arquivo")
        if arquivo and str(arquivo).strip():
            arquivo_nome = os.path.basename(str(arquivo))
            arquivo_label = ctk.CTkLabel(
                card,
                text=f"Anexo: {arquivo_nome}",
                font=ctk.CTkFont(size=11),
                text_color=colors.ACCENT_CYAN,
                justify="left",
                wraplength=280,
                cursor="hand2"
            )
            arquivo_label.pack(anchor="w", padx=12, pady=(4, 10))
            arquivo_label.bind("<Button-1>", lambda e, key=arquivo: self._abrir_anexo(key))
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _escolher_arquivo(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Imagens e PDF", "*.jpg;*.jpeg;*.png;*.pdf"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if not path:
            return

        extensao = os.path.splitext(path)[1].lower()
        if extensao not in [".jpg", ".jpeg", ".png", ".pdf"]:
            messagebox.showwarning("Atenção", "Selecione um arquivo JPG, PNG ou PDF.")
            self.arquivo_path = None
            self.lbl_file.configure(text="Nenhum arquivo escolhido")
            return

        self.arquivo_path = path
        self.lbl_file.configure(text=os.path.basename(path))

    def _abrir_anexo(self, arquivo_key):
        if not arquivo_key:
            return

        url = get_url_s3(arquivo_key, expires_in=3600)
        if not url:
            messagebox.showerror("Erro", "Não foi possível gerar o link do anexo.")
            return

        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Erro ao abrir anexo: {e}")
            messagebox.showerror("Erro", "Não foi possível abrir o anexo no navegador.")

    def _on_txt_focus_in(self, _event):
        if self.txt.get("1.0", "end-1c") == self.placeholder:
            self.txt.delete("1.0", "end")
            self.txt.configure(text_color=colors.TEXT_DARK)

    def _on_txt_focus_out(self, _event):
        if not self.txt.get("1.0", "end-1c").strip():
            self.txt.insert("1.0", self.placeholder)
            self.txt.configure(text_color=colors.PLACEHOLDER_TEXT)

    def salvar_prontuario(self):
        nome_pet = self.combo_paciente.get()
        pet_id = self.pets_map.get(nome_pet)
        if not pet_id:
            messagebox.showwarning("Atenção", "Selecione um paciente antes de salvar.")
            return

        texto = self.txt.get("1.0", "end-1c").strip()
        if not texto or texto == self.placeholder:
            messagebox.showwarning("Atenção", "Preencha a evolução clínica antes de salvar.")
            return

        arquivo_path = self.arquivo_path

        def tarefa():
            arquivo_key = None
            if arquivo_path:
                arquivo_key = upload_prontuario_arquivo_s3(arquivo_path, pet_id)
                if not arquivo_key:
                    return False, None
            sucesso = self.controller.salvar(pet_id, texto, arquivo_key)
            historico = self.controller.historico(pet_id) if sucesso else None
            return sucesso, historico

        run_backend_task(
            self.content,
            tarefa,
            on_success=self._finalizar_salvar_prontuario,
            on_error=lambda erro: messagebox.showerror("Erro", f"Nao foi possivel salvar o prontuario: {erro}"),
            message="Salvando prontuario...",
        )
        return

        arquivo_key = None
        if self.arquivo_path:
            arquivo_key = upload_prontuario_arquivo_s3(self.arquivo_path, pet_id)
            if not arquivo_key:
                messagebox.showerror("Erro", "Falha ao enviar o arquivo para a nuvem.")
                return

        sucesso = self.controller.salvar(pet_id, texto, arquivo_key)
        if sucesso:
            messagebox.showinfo("Sucesso", "Prontuário salvo com sucesso!")
            self.arquivo_path = None
            self.lbl_file.configure(text="Nenhum arquivo escolhido")
            self._renderizar_historico(self.controller.historico(pet_id))
        else:
            messagebox.showerror("Erro", "Não foi possível salvar o prontuário.")
    def _finalizar_salvar_prontuario(self, resultado):
        sucesso, historico = resultado
        if sucesso:
            messagebox.showinfo("Sucesso", "Prontuario salvo com sucesso!")
            self.arquivo_path = None
            self.lbl_file.configure(text="Nenhum arquivo escolhido")
            self._renderizar_historico(historico)
        else:
            messagebox.showerror("Erro", "Nao foi possivel salvar o prontuario.")
