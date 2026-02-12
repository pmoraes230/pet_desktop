import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from ..controllers.agenda_controller import AgendaController
from ..utils.agenda_utils import AgendaUtils
from .modal_agendamento import ModalAgendamento

class ModuloAgenda:
    def __init__(self, content_frame):
        self.content = content_frame
        self.mes_atual = datetime.now().month
        self.ano_atual = datetime.now().year
        self.dia_selecionado = datetime.now().day
        self.semana_atual = self._obter_semana_atual()
        self.consultas_selecionadas = []
        self.controller = AgendaController()
        self.utils = AgendaUtils()
        self.dias_buttons = {}

    def _obter_semana_atual(self):
        """Retorna o primeiro dia da semana (segunda-feira)"""
        hoje = datetime(self.ano_atual, self.mes_atual, self.dia_selecionado)
        primeira_semana = hoje - timedelta(days=hoje.weekday())
        return primeira_semana

    def tela_agenda(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header com título e subtítulo
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(header_left, text="Agenda de Consultas", font=("Arial", 24, "bold")).pack(anchor="w")
        ctk.CTkLabel(header_left, text="Gerencie seus horários e procedimentos", 
                    font=("Arial", 12), text_color="#999999").pack(anchor="w")
        
        btn_agendar = ctk.CTkButton(header, text="+ Agendar Consulta", fg_color="#17A8A8", 
                                     text_color="white", font=("Arial", 12, "bold"), 
                                     corner_radius=20, width=150, height=40,
                                     command=self.abrir_modal_agendamento)
        btn_agendar.pack(side="right")
        
        # Navegação de meses
        self._criar_navegacao_meses(scroll)
        
        # Frame dos dias da semana
        self._criar_calendario(scroll)
        
        # Frame de consultas
        self.consultas_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.consultas_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        titulo_frame = ctk.CTkFrame(self.consultas_frame, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(titulo_frame, text="Compromissos", font=("Arial", 16, "bold")).pack(anchor="w")
        
        self.lista_consultas = ctk.CTkFrame(self.consultas_frame, fg_color="white", 
                                            corner_radius=20, border_width=1, border_color="#E2E8F0")
        self.lista_consultas.pack(fill="both", expand=True, pady=(0, 20))
        
        self._mostrar_mensagem_vazia()

    def _criar_navegacao_meses(self, parent):
        """Cria os botões de navegação de meses"""
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        btn_prev = ctk.CTkButton(nav_frame, text="<", width=30, height=30, 
                                 command=self._semana_anterior, font=("Arial", 16, "bold"),
                                 fg_color="transparent", text_color="#999999")
        btn_prev.pack(side="left", padx=(0, 10))
        
        mes_nome = calendar.month_name[self.mes_atual]
        self.label_mes = ctk.CTkLabel(nav_frame, text=f"{mes_nome} {self.ano_atual}", 
                                      font=("Arial", 16, "bold"))
        self.label_mes.pack(side="left", padx=20)
        
        btn_next = ctk.CTkButton(nav_frame, text=">", width=30, height=30, 
                                 command=self._semana_proxima, font=("Arial", 16, "bold"),
                                 fg_color="transparent", text_color="#999999")
        btn_next.pack(side="left", padx=(10, 0))

    def _criar_calendario(self, parent):
        """Cria o calendário com apenas 7 dias (semana)"""
        dias_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=20, 
                                  border_width=1, border_color="#E2E8F0")
        dias_frame.pack(fill="x", pady=(0, 30))
        dias_frame.columnconfigure((0,1,2,3,4,5,6), weight=1)
        
        # Headers dos dias da semana
        dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        for i, dia in enumerate(dias_semana):
            ctk.CTkLabel(dias_frame, text=dia, font=("Arial", 10, "bold"), 
                        text_color="#CCCCCC").grid(row=0, column=i, pady=10, padx=5)
        
        # Gerar 7 dias da semana
        dias_com_consultas = self.controller.dias_com_consultas(self.mes_atual, self.ano_atual)
        
        for dia_semana in range(7):
            data_dia = self.semana_atual + timedelta(days=dia_semana)
            numero_dia = data_dia.day
            
            self._criar_dia_button(dias_frame, numero_dia, data_dia, dia_semana, 
                                  numero_dia in dias_com_consultas)

    def _criar_dia_button(self, parent, numero_dia, data_dia, dia_semana, tem_consulta):
        """Cria um botão para cada dia da semana"""
        eh_hoje = self.utils.eh_hoje(numero_dia, data_dia.month, data_dia.year)
        
        btn = ctk.CTkButton(parent, text=str(numero_dia), font=("Arial", 18, "bold"),
                           fg_color="transparent", text_color="#666666",
                           hover_color="#F5F5F5", border_width=0,
                           command=lambda: self._selecionar_dia(numero_dia, data_dia))
        btn.grid(row=1, column=dia_semana, pady=10, padx=5, sticky="nsew", ipady=15)
        
        self.dias_buttons[numero_dia] = {
            'button': btn,
            'tem_consulta': tem_consulta,
            'eh_hoje': eh_hoje,
            'data': data_dia
        }
        
        # Aplicar estilo correto
        self._atualizar_estilo_dia(numero_dia)

    def _atualizar_estilo_dia(self, numero_dia):
        """CORREÇÃO DO BUG VERDE: Diferencia Selecionado de Hoje"""
        if numero_dia not in self.dias_buttons:
            return
            
        btn_info = self.dias_buttons[numero_dia]
        btn = btn_info['button']
        
        # Reseta o hover para evitar o bug visual ao focar
        btn.configure(hover_color="#F5F5F5")

        if numero_dia == self.dia_selecionado:
            # DIA SELECIONADO: Verde cheio (Turquesa)
            btn.configure(fg_color="#17A8A8", text_color="white", border_width=0, corner_radius=15)
        elif btn_info['eh_hoje']:
            # HOJE: Apenas a borda verde (não preenche para não confundir com a seleção)
            btn.configure(fg_color="transparent", text_color="#17A8A8", border_width=2, border_color="#17A8A8", corner_radius=15)
        elif btn_info['tem_consulta']:
            # DIA COM CONSULTA: Borda mais fina ou cinza se preferir
            btn.configure(fg_color="transparent", text_color="#666666", border_width=1, border_color="#17A8A8", corner_radius=15)
        else:
            # DIA NORMAL
            btn.configure(fg_color="transparent", text_color="#666666", border_width=0)

    def _selecionar_dia(self, numero_dia, data_dia):
        """Seleciona um dia e carrega as consultas"""
        dia_antigo = self.dia_selecionado
        
        self.dia_selecionado = numero_dia
        self.mes_atual = data_dia.month
        self.ano_atual = data_dia.year
        
        # Atualiza o estilo do dia que saiu e do dia que entrou
        if dia_antigo in self.dias_buttons:
            self._atualizar_estilo_dia(dia_antigo)
        self._atualizar_estilo_dia(numero_dia)
        
        self.consultas_selecionadas = self.controller.buscar_consultas_do_dia(
            numero_dia, self.mes_atual, self.ano_atual
        )
        self._preencher_consultas()

    def _semana_anterior(self):
        """Navega para a semana anterior"""
        self.semana_atual = self.semana_atual - timedelta(days=7)
        self.mes_atual = self.semana_atual.month
        self.ano_atual = self.semana_atual.year
        self.dia_selecionado = None
        self.tela_agenda()

    def _semana_proxima(self):
        """Navega para a próxima semana"""
        self.semana_atual = self.semana_atual + timedelta(days=7)
        self.mes_atual = self.semana_atual.month
        self.ano_atual = self.semana_atual.year
        self.dia_selecionado = None
        self.tela_agenda()

    def _preencher_consultas(self):
        """Preenche a lista com as consultas do dia"""
        for widget in self.lista_consultas.winfo_children():
            widget.destroy()
        
        if not self.consultas_selecionadas:
            self._mostrar_mensagem_vazia()
            return
        
        for consulta in self.consultas_selecionadas:
            self._criar_card_agendamento(
                self.lista_consultas,
                consulta['HORARIO_CONSULTA'],
                consulta['TIPO_DE_CONSULTA'],
                f"Pet ID: {consulta['ID_PET']} | Vet ID: {consulta['ID_VETERINARIO']}"
            )

    def _criar_card_agendamento(self, master, hora, titulo, subtitulo):
        """Cria card de consulta"""
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=15, 
                           border_width=1, border_color="#E2E8F0")
        card.pack(fill="x", pady=8, padx=15)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(content, text="🕒", font=("Arial", 18)).pack(side="left", padx=(0, 15))
        
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(info_frame, text=str(hora), font=("Arial", 14, "bold"), 
                    text_color="#000000").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=titulo, font=("Arial", 13), 
                    text_color="#000000").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=subtitulo, font=("Arial", 11), 
                    text_color="#999999").pack(anchor="w")

    def _mostrar_mensagem_vazia(self):
        """Mostra mensagem quando não há consultas"""
        for widget in self.lista_consultas.winfo_children():
            widget.destroy()
        
        msg_frame = ctk.CTkFrame(self.lista_consultas, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(msg_frame, text="📅", font=("Arial", 40)).pack(pady=(40, 10))
        ctk.CTkLabel(msg_frame, text="Nenhuma consulta agendada para este período.", 
                    font=("Arial", 14), text_color="#999999").pack(pady=(0, 40))
        
    def abrir_modal_agendamento(self):
        """Abre modal de novo agendamento"""
        ModalAgendamento(self.content, callback_refresh=self.tela_agenda)