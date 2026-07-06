import customtkinter as ctk
from datetime import datetime

from app.core.i18n import tr
from app.core.theme import is_dark_mode
from app.utils.loading import run_backend_task
from ..controllers.agendamento_controller import AgendamentoController


class ModalAgendamento:
    def __init__(self, parent, callback_refresh=None, id_veterinario=None, data_inicial=None):
        self.parent = parent
        self.callback_refresh = callback_refresh
        self.id_veterinario = id_veterinario
        self.data_inicial = data_inicial
        self.controller = AgendamentoController(id_veterinario)
        self.janela = None
        self.pets = []

        self.colors = self._theme_colors()

        self.criar_modal()

    def _theme_colors(self):
        if is_dark_mode():
            return {
                "background": "#111827",
                "card": "#1F2937",
                "input_bg": "#1F2937",
                "input_hover": "#374151",
                "border": "#374151",
                "text_main": "#F9FAFB",
                "text_label": "#D1D5DB",
                "placeholder": "#9CA3AF",
                "primary": "#17A8A8",
                "primary_hover": "#148F8F",
                "cancel": "#374151",
                "cancel_hover": "#4B5563",
                "cancel_text": "#F9FAFB",
            }

        return {
            "background": "#FFFFFF",
            "card": "#FFFFFF",
            "input_bg": "#F3F5F7",
            "input_hover": "#E8EEF5",
            "border": "#D4DDE8",
            "text_main": "#1A2F44",
            "text_label": "#7A8A99",
            "placeholder": "#A0ACB9",
            "primary": "#17A8A8",
            "primary_hover": "#148F8F",
            "cancel": "#F3F5F7",
            "cancel_hover": "#EBECEE",
            "cancel_text": "#7A8A99",
        }

    def criar_modal(self):
        self.janela = ctk.CTkToplevel(self.parent)
        self.janela.title(tr("Novo Agendamento"))
        self.janela.geometry("700x620")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=self.colors["background"])

        self.janela.grab_set()
        self.janela.focus_set()

        header_frame = ctk.CTkFrame(self.janela, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(40, 30))

        ctk.CTkLabel(
            header_frame,
            text=tr("Novo Agendamento"),
            font=("Arial", 26, "bold"),
            text_color=self.colors["text_main"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=tr("Escolha o pet e a data"),
            font=("Arial", 13),
            text_color=self.colors["text_label"],
        ).pack(anchor="w", pady=(5, 0))

        ctk.CTkButton(
            self.janela,
            text="X",
            width=35,
            height=35,
            fg_color=self.colors["cancel"],
            text_color=self.colors["cancel_text"],
            command=self.janela.destroy,
            font=("Arial", 16),
            corner_radius=50,
            hover_color=self.colors["cancel_hover"],
        ).place(relx=0.92, rely=0.06, anchor="center")

        container = ctk.CTkScrollableFrame(self.janela, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        def create_label(master, text):
            return ctk.CTkLabel(
                master,
                text=tr(text).upper(),
                font=("Arial", 11, "bold"),
                text_color=self.colors["text_label"],
            )

        create_label(container, "Qual pet?").pack(anchor="w", pady=(0, 8))

        pet_names = [tr("Carregando...")]

        self.combo_pet = ctk.CTkComboBox(
            container,
            values=pet_names,
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            height=45,
            button_color=self.colors["input_bg"],
            button_hover_color=self.colors["input_hover"],
            text_color=self.colors["text_main"],
            placeholder_text_color=self.colors["placeholder"],
            font=("Arial", 12),
        )
        self.combo_pet.pack(fill="x", pady=(0, 25))
        self.combo_pet.set(tr("Selecione um pet..."))
        run_backend_task(
            self.janela,
            lambda: self.controller.listar_pets(self.id_veterinario),
            on_success=self._finalizar_carregamento_pets,
            on_error=lambda erro: self.mostrar_erro(tr("Erro ao carregar pets: {erro}", erro=erro)),
            message=tr("Carregando pets..."),
        )

        row2 = ctk.CTkFrame(container, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 25))
        row2.columnconfigure((0, 1), weight=1)

        col_data = ctk.CTkFrame(row2, fg_color="transparent")
        col_data.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        create_label(col_data, "Data").pack(anchor="w", pady=(0, 8))
        self.entry_data = ctk.CTkEntry(
            col_data,
            placeholder_text="dd/mm/yyyy",
            height=45,
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            text_color=self.colors["text_main"],
            placeholder_text_color=self.colors["placeholder"],
            font=("Arial", 12),
        )
        self.entry_data.pack(fill="x")
        if self.data_inicial:
            self.entry_data.insert(0, self.data_inicial.strftime("%d/%m/%Y"))

        col_hora = ctk.CTkFrame(row2, fg_color="transparent")
        col_hora.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        create_label(col_hora, "Horario").pack(anchor="w", pady=(0, 8))
        self.entry_hora = ctk.CTkEntry(
            col_hora,
            placeholder_text="HH:MM",
            height=45,
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            text_color=self.colors["text_main"],
            font=("Arial", 12),
        )
        self.entry_hora.pack(fill="x")

        create_label(container, "Tipo de Servico").pack(anchor="w", pady=(0, 8))
        self.combo_tipo = ctk.CTkComboBox(
            container,
            values=[tr("Consulta Geral"), tr("Vacinacao"), tr("Limpeza"), tr("Cirurgia"), tr("Ultrassom"), tr("Outros")],
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            height=45,
            text_color=self.colors["text_main"],
            font=("Arial", 12),
            button_color=self.colors["input_bg"],
            button_hover_color=self.colors["input_hover"],
        )
        self.combo_tipo.pack(fill="x", pady=(0, 25))
        self.combo_tipo.set(tr("Consulta Geral"))

        create_label(container, "Observacoes").pack(anchor="w", pady=(0, 8))
        self.text_obs = ctk.CTkTextbox(
            container,
            height=80,
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            text_color=self.colors["text_main"],
            font=("Arial", 12),
        )
        self.text_obs.pack(fill="x", pady=(0, 25))
        self.text_obs.insert("1.0", tr("Descreva brevemente..."))

        btn_frame = ctk.CTkFrame(self.janela, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=(0, 30))
        btn_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text=tr("Cancelar"),
            height=50,
            fg_color=self.colors["cancel"],
            text_color=self.colors["cancel_text"],
            font=("Arial", 14, "bold"),
            corner_radius=12,
            hover_color=self.colors["cancel_hover"],
            command=self.janela.destroy,
            border_width=1,
            border_color=self.colors["border"],
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text=tr("Agendar Agora"),
            height=50,
            fg_color=self.colors["primary"],
            text_color="white",
            font=("Arial", 14, "bold"),
            corner_radius=12,
            hover_color=self.colors["primary_hover"],
            command=self.agendar_consulta,
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _finalizar_carregamento_pets(self, pets):
        self.pets = pets or []
        pet_names = [p["nome"] for p in self.pets] if self.pets else [tr("Nenhum pet disponivel")]
        self.combo_pet.configure(values=pet_names)
        self.combo_pet.set(tr("Selecione um pet...") if self.pets else tr("Nenhum pet disponivel"))

    def agendar_consulta(self):
        if self.combo_pet.get() in [tr("Selecione um pet..."), tr("Nenhum pet disponivel"), ""]:
            self.mostrar_erro(tr("Selecione um pet"))
            return

        if not self.entry_data.get():
            self.mostrar_erro(tr("Preencha a data"))
            return

        if not self.entry_hora.get():
            self.mostrar_erro(tr("Preencha o horario"))
            return

        try:
            pet_nome = self.combo_pet.get()
            id_pet = next(p["id"] for p in self.pets if p["nome"] == pet_nome)
        except Exception:
            self.mostrar_erro(tr("Erro ao extrair dados do pet"))
            return

        try:
            data_str = self.entry_data.get()
            datetime.strptime(data_str, "%d/%m/%Y")
            dia, mes, ano = data_str.split("/")
            data_banco = f"{ano}-{mes}-{dia}"
        except Exception:
            self.mostrar_erro(tr("Data invalida (use dd/mm/aaaa)"))
            return

        try:
            hora_str = self.entry_hora.get()
            datetime.strptime(hora_str, "%H:%M")
        except Exception:
            self.mostrar_erro(tr("Horario invalido (use HH:MM)"))
            return

        tipo_consulta = self._tipo_consulta_para_banco(self.combo_tipo.get())
        observacoes = self.text_obs.get("1.0", "end").strip()
        if observacoes == tr("Descreva brevemente..."):
            observacoes = ""

        def tarefa():
            return self.controller.criar_agendamento(
                id_pet, self.id_veterinario, data_banco, hora_str, tipo_consulta, observacoes
            )

        run_backend_task(
            self.janela,
            tarefa,
            on_success=self._finalizar_agendamento,
            on_error=self._erro_agendamento,
            message=tr("Agendando consulta..."),
        )

    def _finalizar_agendamento(self, resultado):
        sucesso, mensagem = resultado

        if sucesso:
            self.mostrar_sucesso(tr(mensagem))
            if self.callback_refresh:
                self.janela.after(1200, self.callback_refresh)
            self.janela.after(1300, self.janela.destroy)
        else:
            self.mostrar_erro(tr(mensagem))

    def _erro_agendamento(self, erro):
        self.mostrar_erro(tr("Erro ao agendar consulta: {erro}", erro=erro))

    def mostrar_erro(self, mensagem):
        dialog = ctk.CTkToplevel(self.janela)
        dialog.title(tr("Erro"))
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=self.colors["background"])

        frame = ctk.CTkFrame(dialog, fg_color=self.colors["card"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="!", font=("Arial", 50), text_color="#F59E0B").pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=mensagem, font=("Arial", 13, "bold"), text_color=self.colors["text_main"]).pack(pady=5)

        ctk.CTkButton(
            dialog,
            text=tr("Entendi"),
            font=("Arial", 12, "bold"),
            fg_color="#17A8A8",
            text_color="white",
            corner_radius=10,
            height=40,
            command=dialog.destroy,
        ).pack(pady=(10, 0), padx=20, fill="x")

    def _tipo_consulta_para_banco(self, tipo):
        tipos = ["Consulta Geral", "Vacinacao", "Limpeza", "Cirurgia", "Ultrassom", "Outros"]
        for tipo_pt in tipos:
            if tipo == tr(tipo_pt):
                return tipo_pt
        return tipo

    def mostrar_sucesso(self, mensagem):
        dialog = ctk.CTkToplevel(self.janela)
        dialog.title(tr("Sucesso"))
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=self.colors["background"])

        frame = ctk.CTkFrame(dialog, fg_color=self.colors["card"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="OK", font=("Arial", 34, "bold"), text_color="#17A8A8").pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=mensagem, font=("Arial", 13, "bold"), text_color=self.colors["text_main"]).pack(pady=5)

        ctk.CTkButton(
            dialog,
            text=tr("Otimo!"),
            font=("Arial", 12, "bold"),
            fg_color="#17A8A8",
            text_color="white",
            corner_radius=10,
            height=40,
            command=dialog.destroy,
        ).pack(pady=(10, 0), padx=20, fill="x")
