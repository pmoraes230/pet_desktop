import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from app.controllers.agenda_controller import AgendaController
from app.controllers.agendamento_controller import AgendamentoController
from app.utils.agenda_utils import AgendaUtils
from app.views.modal_agendamento import ModalAgendamento
from tkinter import messagebox # Para o placeholder do modal de liberar horários
# from ..controllers.agenda_controller import AgendaController # Removido para simplificar para um mock
# from ..utils.agenda_utils import AgendaUtils # Removido para simplificar para um mock
# from .modal_agendamento import ModalAgendamento # Removido para simplificar para um mock

# Reuso da classe Colors do exemplo anterior, com adições para este módulo
class Colors:
    PRIMARY_DARK = "#2E7D7D"  # Um verde-azulado mais escuro para a sidebar
    PRIMARY = "#4CAF50" # Verde para ícones e destaque (não tão usado aqui)
    PRIMARY_HOVER = "#388E8E"
    NEUTRAL_50 = "#F8F9FA"  # Fundo principal muito claro
    NEUTRAL_100 = "#EAECEF" # Hover em botões claros
    NEUTRAL_200 = "#E0E3E8" # Bordas de cards (usado para cards de compromisso)
    NEUTRAL_300 = "#CCD1D9" # Separadores (usado para o ícone de vazio)
    NEUTRAL_500 = "#6B7280" # Ícones e texto secundário (nomes dos dias, etc)
    TEXT_PRIMARY = "#343A40" # Texto principal escuro (texto dos cards de compromisso)
    TEXT_SECONDARY = "#6C757D" # Texto secundário (subtítulos, descrições)
    DANGER = "#DC3545" # Vermelho para ações perigosas/logout
    SUCCESS = "#28A745" # Verde para sucesso
    SUCCESS_BG = "#E6FFED" # Fundo suave para status de sucesso

    # Cores adicionais para este módulo (foco na segunda imagem)
    ACCENT_GREEN = "#00CEC9" # Verde-água vibrante para destaque (dia selecionado, botões)
    ACCENT_GREEN_HOVER = "#00B0AC"
    GRAY_LIGHT = "#F1F5F9" # Fundo de campos de busca/abas e dias não selecionados do calendário
    TEXT_DARK = "#1E293B" # Títulos e textos importantes (Agenda de Consultas, Compromissos da Semana)
    STATUS_HEALTHY_BG = "#E6FFEE" # Fundo para status saudável
    STATUS_HEALTHY_TEXT = "#10B981" # Texto para status saudável
    STATUS_WARNING_BG = "#FFFBEB" # Fundo para status de alerta
    STATUS_WARNING_TEXT = "#F59E0B" # Texto para status de alerta
    PURPLE_ACCENT = "#9B59B6" # Roxo para o botão "Liberar Horários"
    PURPLE_ACCENT_HOVER = "#8E44AD"
    CALENDAR_DAY_BG = "#F1F5F9" # Fundo dos dias normais no calendário (agora é Gray_light)
    CALENDAR_DAY_TEXT_NORMAL = "#34495E" # Texto dos dias normais (agora é TEXT_PRIMARY para o dia)
    CALENDAR_DAY_TEXT_DISABLED = "#BDC3C7" # Texto de dias de outros meses (se houver)
    SHADOW_COLOR = "#D1D5DB" # Cor para simular sombra sutil

colors = Colors()

# Mocks para AgendaController, AgendaUtils e ModalAgendamento para que o código possa ser executado
class MockAgendaController:
    def buscar_consultas_do_dia(self, day, month, year):
        # Simula algumas consultas para o dia 10 de Junho de 2026
        if day == 10 and month == 6 and year == 2026:
            return [
                {'HORARIO_CONSULTA': '10:00', 'TIPO_DE_CONSULTA': 'Consulta de Rotina', 'ID_PET': 123, 'ID_VETERINARIO': 1},
                {'HORARIO_CONSULTA': '14:30', 'TIPO_DE_CONSULTA': 'Vacinação', 'ID_PET': 456, 'ID_VETERINARIO': 1},
            ]
        return []
    def dias_com_consultas_na_semana(self, start_date):
        # Simula que o dia 10 tem consulta
        return {datetime(2026, 6, 10).date()}

class MockAgendaUtils:
    def eh_hoje(self, day, month, year):
        hoje = datetime.now()
        # Simula que "hoje" é o dia 8 de Junho de 2026 para fins de teste
        return day == 8 and month == 6 and year == 2026 # Força o "hoje" ser o dia 8

class MockModalAgendamento:
    def __init__(self, master, callback_refresh):
        self.master = master
        self.callback_refresh = callback_refresh
        messagebox.showinfo("Agendamento", "Modal de agendamento aberto!")
        self.callback_refresh() # Simula o refresh

class ModuloAgenda:
    def __init__(self, content_frame, vet_id=None):
        self.content = content_frame
        self.vet_id = vet_id
        
        # Define o mês e ano iniciais para o exemplo (Junho 2026)
        hoje = datetime.now()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year
        self.dia_selecionado = hoje.day
        
        self.semana_atual_start_date = self._obter_semana_atual_start_date()
        self.consultas_selecionadas = []
        self.controller = AgendaController(self.vet_id)
        self.utils = AgendaUtils()
        # self.modal_agendamento_class = MockModalAgendamento # Usando o mock
        self.dias_buttons = {}

    def _obter_semana_atual_start_date(self):
        """Retorna o primeiro dia da semana (segunda-feira) para a semana do dia selecionado"""
        hoje = datetime(self.ano_atual, self.mes_atual, self.dia_selecionado)
        primeira_semana = hoje - timedelta(days=hoje.weekday())
        return primeira_semana

    def tela_agenda(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Header com título, subtítulo e botões
        header_area = ctk.CTkFrame(scroll, fg_color="transparent")
        header_area.pack(fill="x", pady=(0, 20))
        
        header_left = ctk.CTkFrame(header_area, fg_color="transparent")
        header_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            header_left, 
            text="Agenda de Consultas", 
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_left, 
            text="Gerencie seus horários e procedimentos", 
            font=ctk.CTkFont(family="Helvetica", size=14), 
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 10))
        
        # Botões da direita
        buttons_right_frame = ctk.CTkFrame(header_area, fg_color="transparent")
        buttons_right_frame.pack(side="right")

        btn_liberar_horarios = ctk.CTkButton(
            buttons_right_frame,
            text="Liberar Horários",
            fg_color=colors.PURPLE_ACCENT,
            hover_color=colors.PURPLE_ACCENT_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=10,
            width=150, height=45,
            command=self.abrir_modal_liberar_horarios
        )
        btn_liberar_horarios.pack(side="left", padx=(0, 15))

        btn_marcar_retorno = ctk.CTkButton(
            buttons_right_frame,
            text="+ Marcar retorno",
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=10,
            width=150, height=45,
            command=self.abrir_modal_agendamento
        )
        btn_marcar_retorno.pack(side="left")
        
        # Navegação de mês/semana
        self._criar_navegacao_semanal(scroll)
        
        # Frame dos dias da semana (calendário)
        self._criar_calendario(scroll)
        
        # Título "Compromissos da Semana"
        compromissos_titulo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        compromissos_titulo_frame.pack(fill="x", pady=(30, 10))
        ctk.CTkLabel(
            compromissos_titulo_frame, 
            text="Compromissos da Semana",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w")
        
        # Frame de consultas (Compromissos)
        # Ajuste: A imagem de referência tem um quadro pontilhado ou tracejado quando vazio.
        # Para simular isso, faremos um frame com border_width, border_color e border_spacing=0
        # e um dash_pattern. CustomTkinter não suporta dash_pattern diretamente,
        # então vamos usar um frame simples com a cor de borda.
        self.lista_consultas = ctk.CTkFrame(scroll, fg_color="white", 
                                            corner_radius=20, border_width=1, border_color=colors.NEUTRAL_200) # Bordas mais sutis
        self.lista_consultas.pack(fill="both", expand=True, pady=(0, 20))
        
        # Carrega as consultas para o dia selecionado por padrão
        self.consultas_selecionadas = self.controller.buscar_consultas_do_dia(
            self.dia_selecionado, self.mes_atual, self.ano_atual
        )
        self._preencher_consultas()


    def _criar_navegacao_semanal(self, parent):
        """Cria a barra de navegação semanal com mês e botões de seta."""
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        # Rótulo do Mês/Ano (Junho 2026)
        mes_nome = calendar.month_name[self.mes_atual]
        self.label_mes = ctk.CTkLabel(
            nav_frame, 
            text=f"{mes_nome} {self.ano_atual}", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=colors.TEXT_DARK
        )
        self.label_mes.pack(side="left", padx=(0, 20))
        
        # Botões de navegação da semana
        nav_buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_buttons_frame.pack(side="left", padx=(0,0)) # Adiciona um frame para os botões de nav

        btn_prev = ctk.CTkButton(
            nav_buttons_frame, text="<", width=30, height=30, 
            command=self._semana_anterior, 
            font=ctk.CTkFont(family="Helvetica", size=16),
            fg_color="transparent", 
            text_color=colors.NEUTRAL_500,
            hover_color=colors.NEUTRAL_100,
            corner_radius=8
        )
        btn_prev.pack(side="left", padx=(0, 5))
        
        btn_next = ctk.CTkButton(
            nav_buttons_frame, text=">", width=30, height=30, 
            command=self._semana_proxima, 
            font=ctk.CTkFont(family="Helvetica", size=16),
            fg_color="transparent", 
            text_color=colors.NEUTRAL_500,
            hover_color=colors.NEUTRAL_100,
            corner_radius=8
        )
        btn_next.pack(side="left")


    def _criar_calendario(self, parent):
        """Cria o calendário com apenas 7 dias (semana)"""
        dias_frame = ctk.CTkFrame(
            parent, 
            fg_color="white", # Fundo branco para o container dos dias
            corner_radius=20, # Raio maior para o container principal
            border_width=0
        )
        dias_frame.pack(fill="x", pady=(0, 30))
        dias_frame.columnconfigure((0,1,2,3,4,5,6), weight=1, uniform="week_days")
        
        # Headers dos dias da semana
        dias_semana_nomes = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        for i, dia_nome in enumerate(dias_semana_nomes):
            ctk.CTkLabel(
                dias_frame, 
                text=dia_nome, 
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                text_color=colors.NEUTRAL_500
            ).grid(row=0, column=i, pady=(15, 5), padx=5)
        
        dias_com_consultas = self.controller.dias_com_consultas_na_semana(self.semana_atual_start_date)
        
        for dia_semana_idx in range(7):
            data_dia = self.semana_atual_start_date + timedelta(days=dia_semana_idx)
            
            # Garante que o dia exibido é do mês atual ou simulado
            if data_dia.month != self.mes_atual or data_dia.year != self.ano_atual:
                # Se for de outro mês, podemos pular ou escurecer
                # Para simular a imagem, onde todos os dias estão visíveis e ativos,
                # vamos prosseguir, mas em um calendário completo, aqui haveria tratamento.
                pass 

            self._criar_dia_button(dias_frame, data_dia, dia_semana_idx, 
                                  data_dia.date() in dias_com_consultas)

    def _criar_dia_button(self, parent, data_dia: datetime, dia_semana_idx: int, tem_consulta: bool):
        """Cria um botão para cada dia da semana com o novo estilo."""
        eh_hoje = self.utils.eh_hoje(data_dia.day, data_dia.month, data_dia.year)
        
        # Use um frame para o efeito de "card" e sombra. CustomTkinter não tem sombra nativa.
        # Simulação de sombra: um frame maior e escuro atrás do frame do dia.
        # Isso é uma técnica de UI/UX, pode ser complexo replicar perfeitamente sem libs extras.
        # Para a imagem, parece que a sombra é apenas no dia selecionado.

        # O botão do dia em si
        btn = ctk.CTkButton(
            parent, 
            text=str(data_dia.day), 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            fg_color=colors.GRAY_LIGHT, # Fundo cinza claro para dias não selecionados
            text_color=colors.CALENDAR_DAY_TEXT_NORMAL, # Texto preto para dias não selecionados
            hover_color=colors.NEUTRAL_100, # Hover sutil
            border_width=0,
            corner_radius=10, # Raio menor para o botão do dia
            height=60,
            command=lambda: self._selecionar_dia(data_dia.day, data_dia)
        )
        btn.grid(row=1, column=dia_semana_idx, pady=8, padx=5, sticky="nsew") # Padding ajustado

        # Guarda a referência ao botão e seus dados
        self.dias_buttons[data_dia.strftime("%Y-%m-%d")] = {
            'button': btn,
            'tem_consulta': tem_consulta,
            'eh_hoje': eh_hoje,
            'data': data_dia
        }
        
        # Aplica o estilo inicial (incluindo o dia selecionado e "hoje")
        self._atualizar_estilo_dia(data_dia.strftime("%Y-%m-%d"))

    def _atualizar_estilo_dia(self, data_key: str):
        """Atualiza o estilo de um botão de dia com base no estado."""
        if data_key not in self.dias_buttons:
            return
            
        btn_info = self.dias_buttons[data_key]
        btn = btn_info['button']
        data_dia = btn_info['data']
        
        # Resetar o estilo para o padrão de um dia não selecionado
        btn.configure(
            fg_color=colors.GRAY_LIGHT, # Fundo cinza claro
            text_color=colors.CALENDAR_DAY_TEXT_NORMAL, # Texto preto
            border_width=0, 
            hover_color=colors.NEUTRAL_100
        )
        
        # Lógica para o dia selecionado (com efeito de sombra simulado)
        if data_dia.day == self.dia_selecionado and data_dia.month == self.mes_atual and data_dia.year == self.ano_atual:
            # Para a sombra, o CustomTkinter não suporta diretamente.
            # Uma forma seria criar um frame atrás do botão com um padding,
            # mas isso adiciona complexidade ao grid e pode afetar o layout.
            # Vamos simular a cor mais escura da sombra com uma borda interna
            # ou um fg_color ligeiramente diferente no hover, ou simplesmente
            # focar no fg_color e text_color.
            
            # Para simular a "sombra" ou o "glow" visto na imagem, que é complexo no CTk.
            # Podemos tentar uma borda mais grossa na cor da sombra.
            btn.configure(
                fg_color=colors.ACCENT_GREEN, 
                text_color="white", 
                corner_radius=10,
                border_width=3, # Borda para simular a sombra
                border_color=colors.SHADOW_COLOR # Cor da "sombra"
            )
        elif btn_info['eh_hoje']:
            # HOJE (NÃO SELECIONADO): Borda verde-água sutil
            btn.configure(
                fg_color=colors.GRAY_LIGHT, # Fundo cinza claro como padrão
                text_color=colors.ACCENT_GREEN, # Texto na cor verde-água
                border_width=2, 
                border_color=colors.ACCENT_GREEN, 
                corner_radius=10
            )
        # Se você quiser adicionar um indicador para 'tem_consulta' (a bolinha, por exemplo),
        # precisaria de um frame mais complexo dentro do grid do dia, com um label para o número
        # e outro para a bolinha. Para a imagem atual, não há um indicador visível além da seleção.

    def _selecionar_dia(self, numero_dia, data_dia):
        """Seleciona um dia e carrega as consultas"""
        # Desseleciona o dia antigo
        data_key_antigo = datetime(self.ano_atual, self.mes_atual, self.dia_selecionado).strftime("%Y-%m-%d")
        if data_key_antigo in self.dias_buttons:
            self._atualizar_estilo_dia(data_key_antigo)
        
        self.dia_selecionado = numero_dia
        self.mes_atual = data_dia.month
        self.ano_atual = data_dia.year

        # Atualiza o estilo do novo dia selecionado
        self._atualizar_estilo_dia(data_dia.strftime("%Y-%m-%d"))
        
        self.consultas_selecionadas = self.controller.buscar_consultas_do_dia(
            numero_dia, self.mes_atual, self.ano_atual
        )
        self._preencher_consultas()

    def _semana_anterior(self):
        """Navega para a semana anterior"""
        self.semana_atual_start_date -= timedelta(days=7)
        self.mes_atual = self.semana_atual_start_date.month
        self.ano_atual = self.semana_atual_start_date.year
        self.dia_selecionado = self.semana_atual_start_date.day # Sugere o primeiro dia da semana como selecionado
        self.tela_agenda()

    def _semana_proxima(self):
        """Navega para a próxima semana"""
        self.semana_atual_start_date += timedelta(days=7)
        self.mes_atual = self.semana_atual_start_date.month
        self.ano_atual = self.semana_atual_start_date.year
        self.dia_selecionado = self.semana_atual_start_date.day # Sugere o primeiro dia da semana como selecionado
        self.tela_agenda()

    def _preencher_consultas(self):
        """Preenche a lista com as consultas do dia"""
        for widget in self.lista_consultas.winfo_children():
            widget.destroy()
        
        if not self.consultas_selecionadas:
            self._mostrar_mensagem_vazia()
            return
        
        for consulta in self.consultas_selecionadas:
            subtitulo = consulta.get('NOME_PET') or f"Pet ID: {consulta.get('ID_PET', 'N/A')}"
            status = consulta.get('STATUS')
            observacoes = consulta.get('OBSERVACOES')
            if status:
                subtitulo = f"{subtitulo} | {status}"
            if observacoes:
                subtitulo = f"{subtitulo} | {observacoes}"

            self._criar_card_agendamento(
                self.lista_consultas,
                self._formatar_hora(consulta.get('HORARIO_CONSULTA')),
                consulta.get('TIPO_DE_CONSULTA', 'Consulta'),
                subtitulo
            )

    def _formatar_hora(self, hora):
        if hora is None:
            return "N/A"
        if hasattr(hora, "total_seconds"):
            total = int(hora.total_seconds())
            horas = total // 3600
            minutos = (total % 3600) // 60
            return f"{horas:02d}:{minutos:02d}"
        texto = str(hora)
        return texto[:5] if len(texto) >= 5 else texto

    def _criar_card_agendamento(self, master, hora, titulo, subtitulo):
        """Cria card de consulta com o novo estilo."""
        card = ctk.CTkFrame(
            master, 
            fg_color="white", 
            corner_radius=15, 
            border_width=1, 
            border_color=colors.NEUTRAL_200
        )
        card.pack(fill="x", pady=8, padx=15)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            content, 
            text="🕒", 
            font=("Arial", 22),
            text_color=colors.NEUTRAL_500
        ).pack(side="left", padx=(0, 15))
        
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame, 
            text=str(hora), 
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), 
            text_color=colors.TEXT_PRIMARY
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_frame, 
            text=titulo, 
            font=ctk.CTkFont(family="Helvetica", size=13), 
            text_color=colors.TEXT_PRIMARY
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_frame, 
            text=subtitulo, 
            font=ctk.CTkFont(family="Helvetica", size=11), 
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w")

    def _mostrar_mensagem_vazia(self):
        """Mostra mensagem quando não há consultas com o novo estilo."""
        for widget in self.lista_consultas.winfo_children():
            widget.destroy()
        
        msg_frame = ctk.CTkFrame(self.lista_consultas, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            msg_frame, 
            text="📅", 
            font=("Arial", 60),
            text_color=colors.NEUTRAL_300
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            msg_frame, 
            text="Nenhuma consulta agendada para este período.", 
            font=ctk.CTkFont(family="Helvetica", size=14), 
            text_color=colors.TEXT_SECONDARY
        ).pack(pady=(0, 40))
        
    def abrir_modal_agendamento(self):
        """Abre modal de novo agendamento (Marcar Retorno)"""
        ModalAgendamento(self.content, callback_refresh=self.tela_agenda, id_veterinario=self.vet_id)

    def abrir_modal_liberar_horarios(self):
        """Implementar a lógica para liberar horários."""
        self._abrir_modal_liberar_horarios_real()

    def _abrir_modal_liberar_horarios_real(self):
        if not self.vet_id:
            messagebox.showerror("Erro", "Veterinário logado não encontrado.")
            return

        janela = ctk.CTkToplevel(self.content)
        janela.title("Liberar Horários")
        janela.geometry("520x630")
        janela.resizable(False, False)
        janela.configure(fg_color="white")
        janela.transient(self.content.winfo_toplevel())
        janela.grab_set()
        janela.focus_set()

        ctk.CTkLabel(
            janela,
            text="Liberar Horários",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w", padx=32, pady=(32, 6))

        ctk.CTkLabel(
            janela,
            text="Crie horários livres para os tutores agendarem.",
            font=ctk.CTkFont(size=13),
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w", padx=32, pady=(0, 24))

        def criar_input(label, placeholder):
            ctk.CTkLabel(
                janela,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=colors.TEXT_SECONDARY
            ).pack(anchor="w", padx=32, pady=(0, 6))
            entry = ctk.CTkEntry(
                janela,
                placeholder_text=placeholder,
                height=42,
                corner_radius=10,
                fg_color=colors.GRAY_LIGHT,
                border_width=0
            )
            entry.pack(fill="x", padx=32, pady=(0, 14))
            return entry

        entry_data = criar_input("Data", "DD/MM/AAAA")
        entry_inicio = criar_input("Hora inicial", "HH:MM")
        entry_fim = criar_input("Hora final", "HH:MM")
        entry_intervalo = criar_input("Intervalo em minutos", "30")
        entry_intervalo.insert(0, "30")

        def salvar():
            data_text = entry_data.get().strip()
            hora_inicio_text = entry_inicio.get().strip()
            hora_fim_text = entry_fim.get().strip()
            intervalo_text = entry_intervalo.get().strip()

            if not data_text or data_text == "DD/MM/AAAA" or not hora_inicio_text or not hora_fim_text:
                messagebox.showerror("Erro", "Preencha data e horários corretamente.")
                return

            try:
                data_obj = datetime.strptime(data_text, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Erro", "Data inválida. Use DD/MM/AAAA.")
                return

            try:
                inicio_obj = datetime.strptime(hora_inicio_text, "%H:%M")
                fim_obj = datetime.strptime(hora_fim_text, "%H:%M")
            except ValueError:
                messagebox.showerror("Erro", "Horário inválido. Use HH:MM.")
                return

            if inicio_obj >= fim_obj:
                messagebox.showerror("Erro", "A hora inicial deve ser menor que a hora final.")
                return

            try:
                intervalo = int(intervalo_text)
                if intervalo <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Intervalo inválido. Use um número inteiro maior que zero.")
                return

            controller = AgendamentoController(self.vet_id)
            criados = controller.liberar_horarios(
                self.vet_id,
                data_obj.strftime("%Y-%m-%d"),
                hora_inicio_text,
                hora_fim_text,
                intervalo
            )

            if criados > 0:
                messagebox.showinfo("Sucesso", f"{criados} horário(s) liberado(s).")
                janela.destroy()
                self.tela_agenda()
            else:
                messagebox.showwarning("Aviso", "Nenhum horário novo foi liberado.")

        btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
        btn_frame.pack(fill="x", padx=32, pady=(8, 24))
        btn_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=44,
            fg_color=colors.GRAY_LIGHT,
            hover_color=colors.NEUTRAL_200,
            text_color=colors.TEXT_PRIMARY,
            command=janela.destroy
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Liberar",
            height=44,
            fg_color=colors.PURPLE_ACCENT,
            hover_color=colors.PURPLE_ACCENT_HOVER,
            text_color="white",
            command=salvar
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))
