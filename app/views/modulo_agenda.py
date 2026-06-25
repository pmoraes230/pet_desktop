import calendar
from datetime import datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk

from ..controllers.agenda_controller import AgendaController
from app.core.i18n import tr
from .modal_agendamento import ModalAgendamento


class Colors:
    ACCENT_GREEN = "#26C2B9"
    ACCENT_GREEN_HOVER = "#1EB0A8"
    BORDER = "#E5E7EB"
    CARD = "#FFFFFF"
    DANGER_BG = "#FEE2E2"
    DANGER_TEXT = "#B91C1C"
    GRAY_LIGHT = "#F3F4F6"
    MUTED = "#6B7280"
    PURPLE = "#7C3AED"
    PURPLE_HOVER = "#6D28D9"
    SUCCESS_BG = "#DCFCE7"
    SUCCESS_TEXT = "#166534"
    TEXT = "#1F2937"
    WARNING_BG = "#FEF3C7"
    WARNING_TEXT = "#92400E"


colors = Colors()


class ModuloAgenda:
    def __init__(self, content_frame, id_veterinario=None):
        self.content = content_frame
        self.id_veterinario = id_veterinario
        self.controller = AgendaController(id_veterinario)
        self.modal_horarios = None
        self.calendario_modal = None

        hoje = datetime.now()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year
        self.dia_selecionado = hoje.day
        self.semana_atual_start_date = self._obter_semana_atual_start_date(hoje)
        self.consultas_selecionadas = []

    def _obter_semana_atual_start_date(self, data_base=None):
        data_base = data_base or datetime(self.ano_atual, self.mes_atual, self.dia_selecionado)
        dias_desde_domingo = (data_base.weekday() + 1) % 7
        return data_base - timedelta(days=dias_desde_domingo)

    def tela_agenda(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=30)

        self._criar_header(scroll)
        self._criar_navegacao_semanal(scroll)
        self._criar_calendario(scroll)

        titulo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(30, 10))
        ctk.CTkLabel(
            titulo_frame,
            text=tr("Compromissos da Semana"),
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=colors.TEXT,
        ).pack(anchor="w")

        self.lista_consultas = ctk.CTkFrame(scroll, fg_color="transparent")
        self.lista_consultas.pack(fill="both", expand=True, pady=(0, 20))

        self._carregar_consultas_da_semana()

    def _criar_header(self, parent):
        header_area = ctk.CTkFrame(parent, fg_color="transparent")
        header_area.pack(fill="x", pady=(0, 24))

        header_left = ctk.CTkFrame(header_area, fg_color="transparent")
        header_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            header_left,
            text=tr("Agenda de Consultas"),
            font=ctk.CTkFont(family="Helvetica", size=30, weight="bold"),
            text_color=colors.TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_left,
            text=tr("Gerencie seus horarios e procedimentos"),
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=colors.MUTED,
        ).pack(anchor="w", pady=(3, 0))

        buttons_right_frame = ctk.CTkFrame(header_area, fg_color="transparent")
        buttons_right_frame.pack(side="right")

        ctk.CTkButton(
            buttons_right_frame,
            text=tr("Liberar Horarios"),
            fg_color=colors.PURPLE,
            hover_color=colors.PURPLE_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=16,
            width=160,
            height=48,
            command=self.abrir_modal_liberar_horarios,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            buttons_right_frame,
            text=tr("Calendario"),
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.TEXT,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=16,
            width=130,
            height=48,
            command=self.abrir_calendario_completo,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            buttons_right_frame,
            text=tr("+ Marcar retorno"),
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=16,
            width=160,
            height=48,
            command=self.abrir_modal_agendamento,
        ).pack(side="left")

    def _criar_navegacao_semanal(self, parent):
        nav_frame = ctk.CTkFrame(
            parent,
            fg_color=colors.CARD,
            corner_radius=28,
            border_width=1,
            border_color=colors.BORDER,
        )
        nav_frame.pack(fill="x", pady=(0, 10))

        top = ctk.CTkFrame(nav_frame, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(22, 12))

        mes_nome = self._mes_nome(self.mes_atual)
        ctk.CTkLabel(
            top,
            text=f"{mes_nome} {self.ano_atual}",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=colors.TEXT,
        ).pack(side="left")

        nav_buttons_frame = ctk.CTkFrame(top, fg_color="transparent")
        nav_buttons_frame.pack(side="right")

        for texto, comando in (("<", self._semana_anterior), (">", self._semana_proxima)):
            ctk.CTkButton(
                nav_buttons_frame,
                text=texto,
                width=42,
                height=42,
                command=comando,
                fg_color="transparent",
                text_color=colors.MUTED,
                hover_color=colors.GRAY_LIGHT,
                corner_radius=21,
                font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            ).pack(side="left", padx=(8, 0))

        self._dias_container = nav_frame

    def _criar_calendario(self, parent):
        dias_frame = ctk.CTkFrame(self._dias_container, fg_color="transparent")
        dias_frame.pack(fill="x", padx=20, pady=(0, 24))
        dias_frame.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform="week_days")

        dias_com_consultas = self.controller.dias_com_consultas_na_semana(self.semana_atual_start_date)
        nomes_dias = self._nomes_dias()

        for dia_semana_idx, dia_nome in enumerate(nomes_dias):
            data_dia = self.semana_atual_start_date + timedelta(days=dia_semana_idx)
            self._criar_dia_button(
                dias_frame,
                data_dia,
                dia_nome,
                dia_semana_idx,
                data_dia.date() in dias_com_consultas,
            )

    def _criar_dia_button(self, parent, data_dia, dia_nome, dia_semana_idx, tem_consulta):
        selecionado = (
            data_dia.day == self.dia_selecionado
            and data_dia.month == self.mes_atual
            and data_dia.year == self.ano_atual
        )
        hoje = data_dia.date() == datetime.now().date()

        fg_color = colors.ACCENT_GREEN if selecionado else "#E8FAFA" if hoje else colors.GRAY_LIGHT
        text_color = "white" if selecionado else colors.ACCENT_GREEN if hoje else colors.MUTED
        border_color = colors.ACCENT_GREEN if hoje or tem_consulta else colors.GRAY_LIGHT

        btn = ctk.CTkButton(
            parent,
            text=f"{dia_nome}\n{data_dia.day}",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            fg_color=fg_color,
            text_color=text_color,
            hover_color=colors.ACCENT_GREEN_HOVER if selecionado else "#E5F7F6",
            border_width=2 if hoje or tem_consulta else 0,
            border_color=border_color,
            corner_radius=22,
            height=78,
            command=lambda data=data_dia: self._selecionar_dia(data),
        )
        btn.grid(row=0, column=dia_semana_idx, pady=4, padx=6, sticky="nsew")

    def _selecionar_dia(self, data_dia):
        self.dia_selecionado = data_dia.day
        self.mes_atual = data_dia.month
        self.ano_atual = data_dia.year
        self.tela_agenda()

    def _semana_anterior(self):
        self.semana_atual_start_date -= timedelta(days=7)
        self._selecionar_dia(self.semana_atual_start_date)

    def _semana_proxima(self):
        self.semana_atual_start_date += timedelta(days=7)
        self._selecionar_dia(self.semana_atual_start_date)

    def abrir_calendario_completo(self):
        if self.calendario_modal and self.calendario_modal.winfo_exists():
            self.calendario_modal.lift()
            return

        self.calendario_mes = self.mes_atual
        self.calendario_ano = self.ano_atual

        self.calendario_modal = ctk.CTkToplevel(self.content)
        self.calendario_modal.title(tr("Calendario Completo"))
        self.calendario_modal.geometry("760x650")
        self.calendario_modal.minsize(680, 580)
        self.calendario_modal.configure(fg_color="white")
        self.calendario_modal.grab_set()
        self.calendario_modal.focus_set()

        self.calendario_corpo = ctk.CTkFrame(self.calendario_modal, fg_color="transparent")
        self.calendario_corpo.pack(fill="both", expand=True, padx=32, pady=28)

        self._renderizar_calendario_completo()

    def _renderizar_calendario_completo(self):
        for widget in self.calendario_corpo.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.calendario_corpo, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text=f"{self._mes_nome(self.calendario_mes)} {self.calendario_ano}",
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=colors.TEXT,
        ).pack(side="left")

        botoes = ctk.CTkFrame(header, fg_color="transparent")
        botoes.pack(side="right")

        ctk.CTkButton(
            botoes,
            text="<",
            width=42,
            height=42,
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.MUTED,
            corner_radius=21,
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            command=lambda: self._mudar_mes_calendario(-1),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes,
            text=">",
            width=42,
            height=42,
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.MUTED,
            corner_radius=21,
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            command=lambda: self._mudar_mes_calendario(1),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes,
            text=tr("Fechar"),
            width=90,
            height=42,
            fg_color=colors.DANGER_BG,
            hover_color="#FECACA",
            text_color=colors.DANGER_TEXT,
            corner_radius=14,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            command=self.calendario_modal.destroy,
        ).pack(side="left")

        grade = ctk.CTkFrame(
            self.calendario_corpo,
            fg_color=colors.CARD,
            corner_radius=26,
            border_width=1,
            border_color=colors.BORDER,
        )
        grade.pack(fill="both", expand=True)
        grade.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform="calendar_days")

        nomes_dias = self._nomes_dias()
        for coluna, nome in enumerate(nomes_dias):
            ctk.CTkLabel(
                grade,
                text=nome,
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                text_color=colors.MUTED,
            ).grid(row=0, column=coluna, padx=8, pady=(18, 8), sticky="ew")

        resumo_mes = self.controller.resumo_calendario_mes(self.calendario_mes, self.calendario_ano)

        for linha, semana in enumerate(resumo_mes["semanas"], start=1):
            grade.rowconfigure(linha, weight=1, uniform="calendar_rows")
            for coluna, dia_info in enumerate(semana):
                self._criar_dia_mes_button(grade, dia_info, linha, coluna)

    def _criar_dia_mes_button(self, parent, dia_info, linha, coluna):
        data_dia = dia_info["data"]
        tem_consulta = dia_info["tem_consulta"]
        data_atual = datetime.now().date()
        data_selecionada = datetime(self.ano_atual, self.mes_atual, self.dia_selecionado).date()
        fora_do_mes = dia_info["fora_do_mes"]
        selecionado = data_dia == data_selecionada
        hoje = data_dia == data_atual

        fg_color = colors.ACCENT_GREEN if selecionado else "#E8FAFA" if hoje else colors.GRAY_LIGHT
        text_color = "white" if selecionado else colors.ACCENT_GREEN if hoje or tem_consulta else colors.TEXT
        if fora_do_mes:
            fg_color = "#FAFAFA"
            text_color = "#CBD5E1"

        texto = str(data_dia.day)
        if tem_consulta and not fora_do_mes:
            texto = f"{data_dia.day}\n{dia_info['total_consultas']}"

        ctk.CTkButton(
            parent,
            text=texto,
            height=70,
            fg_color=fg_color,
            hover_color="#E5F7F6" if not fora_do_mes else "#FAFAFA",
            text_color=text_color,
            border_width=2 if (hoje or tem_consulta) and not fora_do_mes else 0,
            border_color=colors.ACCENT_GREEN if hoje or tem_consulta else colors.GRAY_LIGHT,
            corner_radius=18,
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            command=lambda data=data_dia: self._selecionar_dia_calendario(data),
        ).grid(row=linha, column=coluna, padx=8, pady=8, sticky="nsew")

    def _mudar_mes_calendario(self, direcao):
        novo_mes = self.calendario_mes + direcao
        if novo_mes < 1:
            self.calendario_mes = 12
            self.calendario_ano -= 1
        elif novo_mes > 12:
            self.calendario_mes = 1
            self.calendario_ano += 1
        else:
            self.calendario_mes = novo_mes

        self._renderizar_calendario_completo()

    def _selecionar_dia_calendario(self, data_dia):
        data_datetime = datetime(data_dia.year, data_dia.month, data_dia.day)
        self.semana_atual_start_date = self._obter_semana_atual_start_date(data_datetime)
        self.dia_selecionado = data_dia.day
        self.mes_atual = data_dia.month
        self.ano_atual = data_dia.year
        if self.calendario_modal and self.calendario_modal.winfo_exists():
            self.calendario_modal.destroy()
        self.tela_agenda()

    def _carregar_consultas_da_semana(self):
        self.consultas_selecionadas = self.controller.buscar_consultas_da_semana(self.semana_atual_start_date)
        self._preencher_consultas()

    def _preencher_consultas(self):
        for widget in self.lista_consultas.winfo_children():
            widget.destroy()

        if not self.consultas_selecionadas:
            self._mostrar_mensagem_vazia()
            return

        for consulta in self.consultas_selecionadas:
            self._criar_card_agendamento(self.lista_consultas, consulta)

    def _criar_card_agendamento(self, master, consulta):
        hora = self._formatar_hora(consulta.get("HORARIO_CONSULTA"))
        data = self._formatar_data_curta(consulta.get("DATA_CONSULTA"))
        titulo = tr(consulta.get("TIPO_DE_CONSULTA") or "Consulta")
        pet_nome = consulta.get("NOME_PET") or f"Pet ID: {consulta.get('ID_PET', 'N/A')}"
        tutor_nome = consulta.get("NOME_TUTOR") or tr("Nao informado")
        status_raw = consulta.get("STATUS") or "Sem status"
        status = tr(status_raw)

        card = ctk.CTkFrame(
            master,
            fg_color=colors.CARD,
            corner_radius=28,
            border_width=1,
            border_color=colors.BORDER,
        )
        card.pack(fill="x", pady=8)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=22, pady=18)

        data_frame = ctk.CTkFrame(content, fg_color="transparent", width=96)
        data_frame.pack(side="left", padx=(0, 20), fill="y")
        data_frame.pack_propagate(False)

        ctk.CTkLabel(
            data_frame,
            text=data,
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.PURPLE,
        ).pack(anchor="center")

        ctk.CTkLabel(
            data_frame,
            text=hora,
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=colors.TEXT,
        ).pack(anchor="center", pady=(4, 0))

        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text=titulo,
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=colors.TEXT,
        ).pack(side="left", anchor="w")

        badge_bg, badge_text = self._cores_status(status)
        ctk.CTkLabel(
            title_row,
            text=status,
            fg_color=badge_bg,
            text_color=badge_text,
            corner_radius=12,
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            width=96,
            height=26,
        ).pack(side="left", padx=(12, 0))

        ctk.CTkLabel(
            info_frame,
            text=f"{pet_nome}  |  {tr('Tutor')}: {tutor_nome}",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=colors.MUTED,
        ).pack(anchor="w", pady=(5, 0))

        acoes = ctk.CTkFrame(info_frame, fg_color="transparent")
        acoes.pack(anchor="w", pady=(14, 0))

        status_norm = self._status_normalizado(status_raw)
        if status_norm == "pendente":
            self._criar_botao_acao(acoes, tr("Aceitar"), colors.SUCCESS_TEXT, "#15803D", lambda: self._mudar_status(consulta, "Confirmado"))
            self._criar_botao_acao(acoes, tr("Rejeitar"), colors.DANGER_TEXT, "#991B1B", lambda: self._mudar_status(consulta, "Cancelado"))
        if status_norm == "confirmado":
            self._criar_botao_acao(acoes, tr("Finalizar Consulta"), colors.PURPLE, colors.PURPLE_HOVER, lambda: self._mudar_status(consulta, "Concluido"))

        self._criar_botao_acao(acoes, tr("Detalhes"), colors.GRAY_LIGHT, "#E5E7EB", lambda: self._abrir_modal_detalhes(consulta), text_color=colors.MUTED)
        self._criar_botao_acao(acoes, tr("Excluir"), colors.DANGER_BG, "#FECACA", lambda: self._confirmar_exclusao(consulta), text_color=colors.DANGER_TEXT)

    def _criar_botao_acao(self, parent, texto, cor, hover, comando, text_color="white"):
        ctk.CTkButton(
            parent,
            text=texto,
            fg_color=cor,
            hover_color=hover,
            text_color=text_color,
            height=34,
            corner_radius=12,
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            command=comando,
        ).pack(side="left", padx=(0, 8))

    def _cores_status(self, status):
        status_normalizado = self._status_normalizado(status)
        if status_normalizado in ("confirmado", "concluido"):
            return colors.SUCCESS_BG, colors.SUCCESS_TEXT
        if status_normalizado == "pendente":
            return colors.WARNING_BG, colors.WARNING_TEXT
        if status_normalizado == "cancelado":
            return colors.DANGER_BG, colors.DANGER_TEXT
        return colors.GRAY_LIGHT, colors.MUTED

    def _mostrar_mensagem_vazia(self):
        msg_frame = ctk.CTkFrame(
            self.lista_consultas,
            fg_color=colors.CARD,
            corner_radius=30,
            border_width=2,
            border_color=colors.BORDER,
        )
        msg_frame.pack(fill="x", expand=True)

        ctk.CTkLabel(
            msg_frame,
            text=tr("Nenhuma consulta agendada para este periodo."),
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.MUTED,
        ).pack(pady=64)

    def _status_normalizado(self, status):
        return (status or "").lower().replace("í", "i").replace("Ã­", "i")

    def _formatar_hora(self, valor):
        if not valor:
            return "--:--"
        if hasattr(valor, "strftime"):
            return valor.strftime("%H:%M")
        return str(valor)[:5]

    def _como_data(self, valor):
        if not valor:
            return None
        if hasattr(valor, "date"):
            return valor.date()
        return valor

    def _formatar_data_curta(self, valor):
        if not valor:
            return "--"
        data = self._como_data(valor)
        meses = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"] if tr("Idioma") == "Language" else ["", "JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        return f"{data.day:02d} {meses[data.month]}"

    def _formatar_data_longa(self, valor):
        if not valor:
            return "--"
        data = self._como_data(valor)
        return data.strftime("%d/%m/%Y")

    def _mes_nome(self, mes):
        nomes = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"] if tr("Idioma") == "Language" else ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        return nomes[mes] if 1 <= mes <= 12 else calendar.month_name[mes]

    def _nomes_dias(self):
        if tr("Idioma") == "Language":
            return ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        return ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]

    def _mudar_status(self, consulta, novo_status):
        status_atual = self._status_normalizado(consulta.get("STATUS"))
        if novo_status == "Confirmado" and status_atual != "pendente":
            messagebox.showwarning(tr("Agenda"), tr("Apenas consultas pendentes podem ser aceitas."))
            return
        if novo_status == "Cancelado" and status_atual != "pendente":
            messagebox.showwarning(tr("Agenda"), tr("Apenas consultas pendentes podem ser rejeitadas."))
            return
        if novo_status == "Concluido" and status_atual != "confirmado":
            messagebox.showwarning(tr("Agenda"), tr("Apenas consultas confirmadas podem ser finalizadas."))
            return

        sucesso, mensagem = self.controller.atualizar_status_consulta(consulta.get("id"), novo_status)
        if sucesso:
            self.tela_agenda()
            messagebox.showinfo(tr("Agenda"), mensagem)
        else:
            messagebox.showerror(tr("Agenda"), mensagem)

    def _confirmar_exclusao(self, consulta):
        pet_nome = consulta.get("NOME_PET") or tr("este pet")
        confirmar = messagebox.askyesno(
            tr("Confirmar exclusao"),
            tr("Tem certeza que deseja excluir a consulta de {pet_nome}? Esta acao nao pode ser desfeita.", pet_nome=pet_nome),
        )
        if not confirmar:
            return

        sucesso, mensagem = self.controller.excluir_consulta(consulta.get("id"))
        if sucesso:
            self.tela_agenda()
            messagebox.showinfo(tr("Agenda"), mensagem)
        else:
            messagebox.showerror(tr("Agenda"), mensagem)

    def _abrir_modal_detalhes(self, consulta):
        modal = ctk.CTkToplevel(self.content)
        modal.title(tr("Detalhes do Agendamento"))
        modal.geometry("520x500")
        modal.resizable(False, False)
        modal.configure(fg_color="white")
        modal.grab_set()
        modal.focus_set()

        header = ctk.CTkFrame(modal, fg_color=colors.ACCENT_GREEN, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=tr(consulta.get("TIPO_DE_CONSULTA") or "Consulta"),
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color="white",
        ).pack(anchor="w", padx=32, pady=(28, 4))

        ctk.CTkLabel(
            header,
            text=tr("Informacoes do agendamento"),
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color="#E8FFFF",
        ).pack(anchor="w", padx=32, pady=(0, 28))

        body = ctk.CTkFrame(modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=28)
        body.columnconfigure((0, 1), weight=1)

        self._detalhe_item(body, tr("Paciente"), consulta.get("NOME_PET") or tr("Nao informado"), 0, 0)
        self._detalhe_item(body, tr("Tutor"), consulta.get("NOME_TUTOR") or tr("Nao informado"), 0, 1)
        self._detalhe_item(body, tr("Data"), self._formatar_data_longa(consulta.get("DATA_CONSULTA")), 1, 0)
        self._detalhe_item(body, tr("Hora"), self._formatar_hora(consulta.get("HORARIO_CONSULTA")), 1, 1)
        self._detalhe_item(body, tr("Status"), tr(consulta.get("STATUS") or "Sem status"), 2, 0)

        ctk.CTkLabel(
            body,
            text=tr("OBSERVACOES"),
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.MUTED,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(18, 8))

        obs = consulta.get("OBSERVACOES") or tr("Nenhuma observacao.")
        ctk.CTkLabel(
            body,
            text=obs,
            fg_color="#E8FAFA",
            text_color=colors.MUTED,
            corner_radius=14,
            justify="left",
            anchor="w",
            wraplength=420,
            height=80,
            font=ctk.CTkFont(family="Helvetica", size=13),
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        ctk.CTkButton(
            body,
            text=tr("Fechar"),
            height=46,
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.MUTED,
            corner_radius=14,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=modal.destroy,
        ).grid(row=5, column=0, columnspan=2, sticky="ew")

    def _detalhe_item(self, parent, label, valor, row, column):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=column, sticky="ew", padx=(0, 12) if column == 0 else (12, 0), pady=(0, 14))

        ctk.CTkLabel(
            frame,
            text=label.upper(),
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.MUTED,
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text=valor,
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=colors.TEXT,
        ).pack(anchor="w", pady=(3, 0))

    def abrir_modal_agendamento(self):
        ModalAgendamento(
            self.content,
            callback_refresh=self.tela_agenda,
            id_veterinario=self.id_veterinario,
        )

    def abrir_modal_liberar_horarios(self):
        self.modal_horarios = ctk.CTkToplevel(self.content)
        self.modal_horarios.title(tr("Liberar Horarios"))
        self.modal_horarios.geometry("500x520")
        self.modal_horarios.resizable(False, False)
        self.modal_horarios.configure(fg_color="white")
        self.modal_horarios.grab_set()
        self.modal_horarios.focus_set()

        header = ctk.CTkFrame(self.modal_horarios, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(36, 24))

        ctk.CTkLabel(
            header,
            text=tr("Liberar Horarios"),
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color=colors.TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=tr("Crie vagas disponiveis para os tutores"),
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color=colors.MUTED,
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            self.modal_horarios,
            text="X",
            width=34,
            height=34,
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.MUTED,
            corner_radius=17,
            command=self.modal_horarios.destroy,
        ).place(relx=0.92, rely=0.06, anchor="center")

        form = ctk.CTkFrame(self.modal_horarios, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)

        self.entry_data_liberar = self._criar_input_horario(
            form,
            tr("Dia da disponibilidade"),
            datetime(self.ano_atual, self.mes_atual, self.dia_selecionado).strftime("%d/%m/%Y"),
        )

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", pady=(0, 22))
        row.columnconfigure((0, 1), weight=1)

        col_inicio = ctk.CTkFrame(row, fg_color="transparent")
        col_inicio.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_inicio_liberar = self._criar_input_horario(col_inicio, tr("Hora de inicio"), "08:00")

        col_fim = ctk.CTkFrame(row, fg_color="transparent")
        col_fim.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        self.entry_fim_liberar = self._criar_input_horario(col_fim, tr("Hora de termino"), "18:00")

        ctk.CTkLabel(
            form,
            text=tr("INTERVALO ENTRE CONSULTAS"),
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.MUTED,
        ).pack(anchor="w", pady=(0, 8))

        self.combo_intervalo_liberar = ctk.CTkComboBox(
            form,
            values=[tr("30 minutos"), tr("60 minutos"), tr("15 minutos"), tr("45 minutos")],
            height=45,
            fg_color=colors.GRAY_LIGHT,
            border_width=0,
            corner_radius=12,
            button_color=colors.GRAY_LIGHT,
            button_hover_color="#E5E7EB",
            text_color=colors.TEXT,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        self.combo_intervalo_liberar.pack(fill="x", pady=(0, 22))
        self.combo_intervalo_liberar.set(tr("30 minutos"))

        self.label_feedback_liberar = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=colors.MUTED,
        )
        self.label_feedback_liberar.pack(fill="x", pady=(0, 12))

        botoes = ctk.CTkFrame(self.modal_horarios, fg_color="transparent")
        botoes.pack(fill="x", padx=40, pady=(0, 30))
        botoes.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            botoes,
            text=tr("Cancelar"),
            height=48,
            fg_color=colors.GRAY_LIGHT,
            hover_color="#E5E7EB",
            text_color=colors.MUTED,
            corner_radius=12,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=self.modal_horarios.destroy,
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            botoes,
            text=tr("Criar vagas"),
            height=48,
            fg_color=colors.PURPLE,
            hover_color=colors.PURPLE_HOVER,
            text_color="white",
            corner_radius=12,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=self._salvar_horarios_liberados,
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _criar_input_horario(self, parent, label, valor_padrao):
        ctk.CTkLabel(
            parent,
            text=label.upper(),
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=colors.MUTED,
        ).pack(anchor="w", pady=(0, 8))

        entry = ctk.CTkEntry(
            parent,
            height=45,
            fg_color=colors.GRAY_LIGHT,
            border_width=0,
            corner_radius=12,
            text_color=colors.TEXT,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        entry.pack(fill="x", pady=(0, 22))
        entry.insert(0, valor_padrao)
        return entry

    def _salvar_horarios_liberados(self):
        intervalo = self.combo_intervalo_liberar.get().split()[0]
        sucesso, mensagem, criados, existentes = self.controller.liberar_horarios(
            self.entry_data_liberar.get().strip(),
            self.entry_inicio_liberar.get().strip(),
            self.entry_fim_liberar.get().strip(),
            intervalo,
        )

        if not sucesso:
            self.label_feedback_liberar.configure(text=mensagem, text_color=colors.DANGER_TEXT)
            return

        texto = tr("{criados} horario(s) criado(s).", criados=criados)
        if existentes:
            texto += tr(" {existentes} ja existiam.", existentes=existentes)
        self.label_feedback_liberar.configure(text=texto, text_color=colors.SUCCESS_TEXT)
        self.content.after(900, self.modal_horarios.destroy)
        self.content.after(950, self.tela_agenda)
