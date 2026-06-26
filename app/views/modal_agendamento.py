import customtkinter as ctk
from datetime import datetime

from app.core.i18n import tr
from ..controllers.agendamento_controller import AgendamentoController


class ModalAgendamento:
    def __init__(self, parent, callback_refresh=None, id_veterinario=None):
        self.parent = parent
        self.callback_refresh = callback_refresh
        self.id_veterinario = id_veterinario
        self.controller = AgendamentoController(id_veterinario)
        self.janela = None
        self.pets = []

        self.colors = {
            "background": "#FFFFFF",
            "input_bg": "#F3F5F7",
            "text_main": "#1A2F44",
            "text_label": "#7A8A99",
            "placeholder": "#A0ACB9",
            "primary": "#17A8A8",
            "cancel": "#F3F5F7",
            "cancel_text": "#7A8A99",
        }

        self.criar_modal()

    def criar_modal(self):
        self.janela = ctk.CTkToplevel(self.parent)
        self.janela.title(tr("Novo Agendamento"))
        self.janela.geometry("500x620")
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
            fg_color="#F3F5F7",
            text_color="#666666",
            command=self.janela.destroy,
            font=("Arial", 16),
            corner_radius=50,
            hover_color="#E8EEF5",
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

        self.pets = self.controller.listar_pets(self.id_veterinario)
        pet_names = [p["nome"] for p in self.pets] if self.pets else [tr("Nenhum pet disponivel")]

        self.combo_pet = ctk.CTkComboBox(
            container,
            values=pet_names,
            fg_color=self.colors["input_bg"],
            border_width=0,
            corner_radius=12,
            height=45,
            button_color=self.colors["input_bg"],
            button_hover_color="#E8EEF5",
            text_color=self.colors["text_main"],
            font=("Arial", 12),
        )
        self.combo_pet.pack(fill="x", pady=(0, 25))
        self.combo_pet.set(tr("Selecione um pet..."))

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
            font=("Arial", 12),
        )
        self.entry_data.pack(fill="x")

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
            button_hover_color="#E8EEF5",
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
            hover_color="#EBECEE",
            command=self.janela.destroy,
            border_width=1,
            border_color="#D4DDE8",
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text=tr("Agendar Agora"),
            height=50,
            fg_color=self.colors["primary"],
            text_color="white",
            font=("Arial", 14, "bold"),
            corner_radius=12,
            hover_color="#148F8F",
            command=self.agendar_consulta,
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

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

        sucesso = self.controller.criar_agendamento(
            id_pet, self.id_veterinario, data_banco, hora_str, tipo_consulta, observacoes
        )

        if sucesso:
            self.mostrar_sucesso(tr("Consulta agendada com sucesso!"))
            if self.callback_refresh:
                self.callback_refresh()
            self.janela.after(1500, self.janela.destroy)
        else:
            self.mostrar_erro(tr("Erro ao agendar consulta no banco de dados"))

    def mostrar_erro(self, mensagem):
        dialog = ctk.CTkToplevel(self.janela)
        dialog.title(tr("Erro"))
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="white")

        frame = ctk.CTkFrame(dialog, fg_color="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="!", font=("Arial", 50), text_color="#F59E0B").pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=mensagem, font=("Arial", 13, "bold"), text_color="#333333").pack(pady=5)

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
        dialog.configure(fg_color="white")

        frame = ctk.CTkFrame(dialog, fg_color="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="OK", font=("Arial", 34, "bold"), text_color="#17A8A8").pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=mensagem, font=("Arial", 13, "bold"), text_color="#333333").pack(pady=5)

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
