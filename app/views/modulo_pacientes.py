import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from app.controllers.pet_controller import PetController
from app.core.i18n import tr
from app.services.s3_client import upload_foto_pet_s3, get_url_s3
import uuid

# Reuso da classe Colors do exemplo anterior
class Colors:
    # Cores ajustadas para combinar com a segunda imagem
    PRIMARY_DARK = "#004D40"  # Verde escuro para a sidebar (mais escuro que o anterior)
    PRIMARY = "#4CAF50" # Verde para ícones e destaque (não tão usado aqui)
    PRIMARY_HOVER = "#00695C" # Hover da sidebar
    NEUTRAL_50 = "#F8F9FA"  # Fundo principal muito claro
    NEUTRAL_100 = "#EAECEF" # Hover em botões claros
    NEUTRAL_200 = "#E0E3E8" # Bordas de cards
    NEUTRAL_300 = "#CCD1D9" # Separadores
    NEUTRAL_500 = "#6B7280" # Ícones e texto secundário
    TEXT_PRIMARY = "#343A40" # Texto principal escuro
    TEXT_SECONDARY = "#6C757D" # Texto secundário
    DANGER = "#DC3545" # Vermelho para ações perigosas/logout
    SUCCESS = "#28A745" # Verde para sucesso
    SUCCESS_BG = "#E6FFED" # Fundo suave para status de sucesso

    # Cores específicas para os novos cards de métricas (não diretamente usadas aqui, mas mantidas)
    METRIC_ICON_1 = "#8A2BE2" # Roxo para Total Pacientes
    METRIC_ICON_2 = "#FFC107" # Amarelo para Consultas Hoje
    METRIC_ICON_3 = "#DC3545" # Vermelho para Casos Críticos
    METRIC_ICON_4 = "#28A745" # Verde para Faturamento Mensal
    
    # Cores adicionais para este módulo (AJUSTADAS)
    ACCENT_GREEN = "#1ABC9C" # Verde brilhante para botões e destaque
    ACCENT_GREEN_HOVER = "#17A689"
    GRAY_LIGHT = "#F1F5F9" # Fundo de campos de busca/abas (AJUSTADO PARA SER MAIS CLARO)
    TEXT_DARK = "#1E293B" # Títulos e textos importantes
    STATUS_HEALTHY_BG = "#E6FFEE" # Fundo para status saudável
    STATUS_HEALTHY_TEXT = "#10B981" # Texto para status saudável
    STATUS_WARNING_BG = "#FFFBEB" # Fundo para status de alerta
    STATUS_WARNING_TEXT = "#F59E0B" # Texto para status de alerta

colors = Colors()


class ModuloPacientes:
    def __init__(self, content_frame, pet_controller: PetController):
        self.content = content_frame
        self.pet_controller = pet_controller
        self.default_pet_image = None  # Para a imagem padrão do pet
        self._load_default_pet_image() # Carrega imagem padrão

    def _load_default_pet_image(self):
        try:
            # Caminho de uma imagem genérica de pet, ou um ícone simples
            assets_dir = Path(__file__).resolve().parents[1] / "assets"
            path = assets_dir / "default_pet.png"
            if not path.exists():
                path = assets_dir / "pet.png"
            # Vou usar um placeholder simples aqui se não houver um asset real.
            # Em um ambiente real, você teria um arquivo default_pet.png ou um ícone.
            # Para este exemplo, vou simular um ícone ou usar o placeholder anterior
            # Caso o asset default_pet.png não exista, o comportamento será o mesmo de antes.
            self.default_pet_image = ctk.CTkImage(Image.open(path), size=(180, 120))
        except FileNotFoundError:
            print("Erro: default_pet.png não encontrado. Usando placeholder de texto.")
            # Cria uma imagem PIL simples com a pata para usar como fallback visual
            # Isso simula o comportamento do "🐾" mas como uma imagem
            img = Image.new('RGBA', (180, 120), (255, 255, 255, 0)) # Imagem transparente
            # Se você tiver um ícone de pata como PNG, pode carregá-lo aqui.
            # Por simplicidade, vou manter a lógica de texto ou um ícone simples
            self.default_pet_image = None

    def _usar_imagem_padrao(self, label, font_size=60):
        if self.default_pet_image:
            label.configure(image=self.default_pet_image, text="")
            label.img_ref = self.default_pet_image
        else:
            label.configure(text="ðŸ¾", font=("Arial", font_size), text_color=colors.NEUTRAL_500)

    def tela_pacientes(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=30) # Padding ajustado

        # Cabeçalho da tela (Pacientes) e descrição
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text=tr("Pacientes"),
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=tr("Gerencie os registros dos animais e tutores"),
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))


        # Campo de busca e botão de filtro
        search_filter_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_filter_row.pack(fill="x", pady=(0, 30))
        search_filter_row.grid_columnconfigure(0, weight=1) # Faz a entrada expandir

        ctk.CTkEntry(
            search_filter_row,
            placeholder_text=f"🔍 {tr('Pesquise por nome do tutor ou nome do pet')}",
            height=45,
            corner_radius=10, # Raio menor
            fg_color=colors.GRAY_LIGHT, # Ajustado para cor da segunda imagem
            border_width=0, # Sem borda
            text_color=colors.TEXT_PRIMARY,
            placeholder_text_color=colors.NEUTRAL_500,
            font=ctk.CTkFont(family="Helvetica", size=14)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ctk.CTkButton(
            search_filter_row,
            text=tr("Filtrar"),
            fg_color=colors.GRAY_LIGHT, # Ajustado para cor da segunda imagem
            hover_color=colors.NEUTRAL_200,
            text_color=colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="normal"),
            height=45,
            corner_radius=10,
            command=self.aplicar_filtro # Implementar função de filtro
        ).grid(row=0, column=1, sticky="e")
        
        # Botão "+ Novo Paciente" - Posicionado separadamente no cabeçalho
        ctk.CTkButton(
            header_frame, # Anexa ao header_frame
            text=tr("+ Novo Paciente"),
            fg_color=colors.ACCENT_GREEN, # Ajustado para cor da segunda imagem
            hover_color=colors.ACCENT_GREEN_HOVER, # Ajustado para cor da segunda imagem
            width=160, # Ajuste de largura
            height=45, # Altura ajustada
            corner_radius=10,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=self.abrir_popup_novo_paciente
        ).pack(side="right", anchor="ne", pady=(0, 20)) # Alinhado à direita do cabeçalho


        # Grid de cards
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1, uniform="pet_cards") # Uniform para colunas de mesmo tamanho

        # Busca os pets reais do banco
        pets = self.pet_controller.listar_pets()
        if not pets:
            ctk.CTkLabel(
                grid,
                text="Nenhum paciente aceito encontrado.",
                font=ctk.CTkFont(family="Helvetica", size=16),
                text_color=colors.TEXT_SECONDARY
            ).grid(row=0, column=0, columnspan=3, pady=40)
            return
        # Simula pets para teste se o controller retornar vazio
        if not pets:
            ctk.CTkLabel(
                grid,
                text=tr("Nenhum paciente aceito por este veterinario."),
                font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
                text_color=colors.TEXT_SECONDARY,
            ).grid(row=0, column=0, columnspan=3, pady=50)
            return
            """
             # DADOS ATUALIZADOS PARA COMBINAR COM A SEGUNDA IMAGEM
             pets = [
                {'id': 1, 'NOME': 'Churrasco', 'ESPECIE': 'cachorro', 'RACA': 'Vira lata', 'DATA_NASCIMENTO': '2020-03-15', 'SEXO': 'Macho', 'PESO': 25.0, 'IMAGEM': 'https://s3.amazonaws.com/coracao-em-patas/imagens/pets/churrasco.jpg', 'DESCRICAO': 'Muito dócil e adora brincar.', 'PERSONALIDADE': 'Brincalhão, Dócil'},
                {'id': 2, 'NOME': 'mini patrick', 'ESPECIE': 'gato', 'RACA': 'vira lata', 'DATA_NASCIMENTO': '2022-12-01', 'SEXO': 'Fêmea', 'PESO': 4.5, 'IMAGEM': 'https://s3.amazonaws.com/coracao-em-patas/imagens/pets/mini_patrick.jpg', 'DESCRICAO': 'Gatinha muito meiga, gosta de carinho.', 'PERSONALIDADE': 'Meigo, Calmo'},
                {'id': 3, 'NOME': 'Missy', 'ESPECIE': 'gato', 'RACA': 'VIRA_LATA', 'DATA_NASCIMENTO': '2023-08-01', 'SEXO': 'Fêmea', 'PESO': 3.2, 'IMAGEM': 'https://s3.amazonaws.com/coracao-em-patas/imagens/pets/missy.jpg', 'DESCRICAO': 'Curiosa e adora explorar.', 'PERSONALIDADE': 'Curioso, Independente'},
                {'id': 4, 'NOME': 'Scooby', 'ESPECIE': 'cachorro', 'RACA': 'Rottweiler', 'DATA_NASCIMENTO': '2021-06-20', 'SEXO': 'Macho', 'PESO': 40.0, 'IMAGEM': 'https://s3.amazonaws.com/coracao-em-patas/imagens/pets/scooby.jpg', 'DESCRICAO': 'Guarda leal e amigável.', 'PERSONALIDADE': 'Protetor, Leal'},
                {'id': 5, 'NOME': 'Zeus', 'ESPECIE': 'cachorro', 'RACA': 'Pastor Alemão', 'DATA_NASCIMENTO': '2020-01-10', 'SEXO': 'Macho', 'PESO': 35.0, 'IMAGEM': 'https://s3.amazonaws.com/coracao-em-patas/imagens/pets/zeus.jpg', 'DESCRICAO': 'Energético e adora correr.', 'PERSONALIDADE': 'Energético, Ativo'}
            ]


            """

        for i, pet in enumerate(pets):
            id_pet = pet.get('id')
            nome = pet.get('NOME', 'Sem nome')
            raca = pet.get('RACA', 'Sem raça').replace('_', ' ').title() # Formata raça
            data_nasc = pet.get('DATA_NASCIMENTO')
            imagem_key = pet.get('IMAGEM')
            
            idade_formatada = self.calcular_idade_formatada(data_nasc)
            
            # Placeholder para status de saúde (sempre "Saudável" por enquanto)
            status_saude = tr("Saudável") 

            self.criar_card_paciente(
                grid,
                id_pet,
                nome,
                status_saude,
                raca,
                idade_formatada,
                imagem_key,
                i // 3,   # linha
                i % 3     # coluna
            )
            
    def aplicar_filtro(self):
        # Implementar lógica de filtragem dos pets
        messagebox.showinfo(tr("Filtro"), tr("Funcionalidade de filtro a ser implementada!"))


    def calcular_idade_formatada(self, data_nasc):
        """Calcula idade em anos e meses a partir da data de nascimento e formata."""
        if not data_nasc:
            return tr("Idade ?")
        try:
            if isinstance(data_nasc, str):
                data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d")
            elif not isinstance(data_nasc, datetime):
                return tr("Idade ?")
            
            hoje = datetime.now()
            
            anos = hoje.year - data_nasc.year
            meses = hoje.month - data_nasc.month
            
            if hoje.day < data_nasc.day:
                meses -= 1
            
            if meses < 0:
                anos -= 1
                meses += 12
            
            partes = []
            if anos > 0:
                partes.append(f"{anos} {tr('anos') if anos > 1 else tr('ano')}")
            if meses > 0:
                partes.append(f"{meses} {tr('meses') if meses > 1 else tr('mes')}")
            
            if not partes:
                return tr("Recém-nascido") if anos == 0 and meses == 0 else tr("Idade ?")
            
            return ", ".join(partes)

        except Exception:
            return tr("Idade ?")


    def criar_card_paciente(self, master, id_pet, nome, status_saude, raca, idade, imagem_key, row, col):
        """Card de paciente com novo design"""
        card = ctk.CTkFrame(
            master,
            fg_color="white",
            corner_radius=16, # Menor raio
            border_width=1,
            border_color=colors.NEUTRAL_200
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew") # Padding ajustado

        # Configura grid interno do card para imagem e texto
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=0) # Imagem
        card.grid_rowconfigure(1, weight=1) # Conteúdo abaixo da imagem

        # Frame para a imagem
        img_placeholder_frame = ctk.CTkFrame(card, fg_color="transparent", height=180, corner_radius=12)
        img_placeholder_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        img_placeholder_frame.grid_propagate(False) # Impede o frame de redimensionar
        img_placeholder_frame.grid_columnconfigure(0, weight=1)
        img_placeholder_frame.grid_rowconfigure(0, weight=1)

        # Label para imagem
        img_label = ctk.CTkLabel(img_placeholder_frame, text="", fg_color=colors.NEUTRAL_100)
        img_label.grid(row=0, column=0, sticky="nsew")
        img_label.img_ref = None # Para guardar a referência da imagem

        # Tentar carregar foto do S3 ou usar a padrão
        self.content.after(100, lambda: self._carregar_foto_card(img_label, imagem_key))

        # Content frame (nome, status, raça, idade)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content_frame,
            text=nome,
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(anchor="w", pady=(0, 5))

        # Status de saúde
        status_frame = ctk.CTkFrame(content_frame, fg_color=colors.STATUS_HEALTHY_BG, corner_radius=10)
        status_frame.pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(
            status_frame,
            text=status_saude,
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=colors.STATUS_HEALTHY_TEXT,
            padx=10, pady=5
        ).pack()

        ctk.CTkLabel(
            content_frame,
            text=raca,
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            content_frame,
            text=idade,
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 15))

        # Botão Ver detalhes
        btn_detalhes = ctk.CTkButton(
            card,
            text=tr("Ver detalhes"),
            fg_color="transparent", # Transparente no fundo do card
            hover_color=colors.NEUTRAL_100, # Hover sutil
            text_color=colors.TEXT_PRIMARY, # Texto escuro
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            corner_radius=10,
            height=40,
            command=lambda pid=id_pet, p_nome=nome, p_raca=raca: self.tela_perfil_pet(pid, p_nome, p_raca, "") # Emoji removido
        )
        btn_detalhes.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15)) # Nova linha para o botão

        # Torna o card clicável
        card.bind("<Button-1>", lambda event, pid=id_pet, p_nome=nome, p_raca=raca: self.tela_perfil_pet(pid, p_nome, p_raca, ""))
        
        return card
        

    def abrir_popup_novo_paciente(self):
        # Abertura do popup deve ser com overlay escuro
        self.overlay = ctk.CTkFrame(self.content.master, fg_color="black") # Cor preta para o overlay
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.modal_frame = ctk.CTkFrame(self.overlay, width=450, height=550, corner_radius=20, 
                                       border_width=0, fg_color="white") # Sem borda
        self.modal_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.modal_frame.pack_propagate(False)

        ctk.CTkLabel(self.modal_frame, text=tr("Novo Paciente"), font=("Helvetica", 24, "bold"), 
                     text_color=colors.TEXT_DARK).pack(pady=(30, 10))

        ctk.CTkLabel(self.modal_frame, text=tr("Preencha os dados do novo paciente"), font=("Helvetica", 13), 
                     text_color=colors.TEXT_SECONDARY).pack(pady=(0, 20))

        form = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        def criar_input(label, placeholder_text):
            ctk.CTkLabel(form, text=label, font=("Helvetica", 12, "bold"), text_color=colors.TEXT_PRIMARY).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(
                form,
                placeholder_text=placeholder_text,
                height=45,
                corner_radius=10,
                border_color=colors.NEUTRAL_200,
                fg_color=colors.GRAY_LIGHT,
                text_color=colors.TEXT_PRIMARY,
                placeholder_text_color=colors.NEUTRAL_500,
                border_width=1 # Adiciona borda sutil
            )
            entry.pack(fill="x", pady=(2, 5))
            return entry

        self.entry_nome_pet = criar_input(tr("Nome do Pet"), "Ex: Rex")
        self.entry_nome_tutor = criar_input(tr("Nome do Tutor"), tr("Ex: Maria Silva"))
        self.entry_telefone_tutor = criar_input(tr("Telefone de Contato"), "Ex: (XX) XXXXX-XXXX")
        self.entry_observacoes = criar_input(tr("Observações Iniciais"), tr("Comportamento, histórico breve..."))

        btn_container = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        btn_container.pack(fill="x", pady=25, padx=30)
        btn_container.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(
            btn_container,
            text=tr("Cancelar"),
            fg_color=colors.NEUTRAL_200,
            hover_color=colors.NEUTRAL_300,
            text_color=colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            width=160, height=45, corner_radius=10,
            command=self.fechar_popup
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            btn_container,
            text=tr("Confirmar"),
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            width=160, height=45, corner_radius=10,
            command=self.salvar_novo_paciente
        ).grid(row=0, column=1, padx=5, sticky="ew")

    def salvar_novo_paciente(self):
        # Implementar lógica para salvar novo paciente
        nome_pet = self.entry_nome_pet.get().strip()
        nome_tutor = self.entry_nome_tutor.get().strip()
        telefone = self.entry_telefone_tutor.get().strip()
        observacoes = self.entry_observacoes.get().strip()

        if not nome_pet or not nome_tutor:
            messagebox.showwarning(tr("Campos Obrigatórios"), tr("Nome do Pet e Nome do Tutor são obrigatórios."))
            return
        
        # Aqui você chamaria seu controlador para salvar no banco
        # Ex: self.pet_controller.adicionar_novo_pet(nome_pet, nome_tutor, telefone, observacoes)
        messagebox.showinfo(tr("Sucesso"), tr("Novo paciente '{nome_pet}' adicionado com sucesso!", nome_pet=nome_pet))
        self.fechar_popup()
        self.tela_pacientes() # Recarrega a lista de pacientes
        

    def fechar_popup(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()

    # Ajuste para a função tela_perfil_pet: removi 'emoji' pois não será mais usado diretamente
    def tela_perfil_pet(self, id_pet, nome_pet, raca_pet, _): 
        # Guardar id do pet para usar nas funções de atualizar foto
        self.pet_atual_id = id_pet
        
        # Buscar dados completos do pet no banco
        pet_dados = self.pet_controller.buscar_pet(id_pet)
        if not pet_dados:
            messagebox.showerror(tr("Erro"), tr("Detalhes do pet não encontrados."))
            self.tela_pacientes()
            return
            
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Layout responsivo
        modo_vertical = self.content.winfo_width() < 1000 or self.content.winfo_width() == 1
        if modo_vertical:
            container.columnconfigure(0, weight=1)
        else:
            container.columnconfigure(0, weight=0)
            container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        if modo_vertical:
            card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=20, # Raio ajustado
                                   border_width=1, border_color=colors.NEUTRAL_200)
            card_esq.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))
        else:
            card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=20, # Raio ajustado
                                   width=350, border_width=1, border_color=colors.NEUTRAL_200)
            card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Container para imagem com botão de mudar
        img_container = ctk.CTkFrame(card_esq, fg_color=colors.NEUTRAL_100, height=220, corner_radius=15) # Cor e raio ajustados
        img_container.pack(fill="x", padx=20, pady=20)
        img_container.pack_propagate(False)
        
        # Frame para a imagem
        self.img_placeholder = ctk.CTkFrame(img_container, fg_color=colors.NEUTRAL_100)
        self.img_placeholder.pack(fill="both", expand=True)
        
        # Label da imagem/emoji (emoji é o fallback)
        self.img_label = ctk.CTkLabel(
            self.img_placeholder, 
            text="🐾", # Emoji padrão
            font=("Arial", 80),
            fg_color=colors.NEUTRAL_100,
            text_color=colors.NEUTRAL_500
        )
        self.img_label.pack(fill="both", expand=True)
        
        # Tentar carregar foto do S3 se existir (com delay para garantir renderização)
        self.content.after(500, lambda: self._carregar_foto_pet_perfil(id_pet))
        
        # Botão para mudar foto (overlay)
        btn_mudar = ctk.CTkButton(
            img_container,
            text=f"📷 {tr('Mudar Foto')}",
            font=("Helvetica", 12, "bold"), # Fonte ajustada
            text_color="white",
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            height=35,
            corner_radius=10,
            command=self.escolher_foto_pet
        )
        btn_mudar.place(relx=0.5, rely=0.9, anchor="center")

        ctk.CTkLabel(card_esq, text=nome_pet, font=("Helvetica", 28, "bold"), text_color=colors.TEXT_DARK).pack(pady=(5, 0))
        ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Helvetica", 11, "bold"), text_color=colors.ACCENT_GREEN).pack(pady=(2, 15))
        
        ctk.CTkLabel(card_esq, text=f"ID: {id_pet}", font=("Helvetica", 10), text_color=colors.NEUTRAL_500).pack(pady=(0, 8))

        # Tutor box
        tutor_box = ctk.CTkFrame(card_esq, fg_color=colors.NEUTRAL_100, corner_radius=15) # Cor ajustada
        tutor_box.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(tutor_box, text=tr("TUTOR RESPONSÁVEL"), font=("Helvetica", 9, "bold"), text_color=colors.NEUTRAL_500).pack(anchor="w", padx=12, pady=(8, 0))
        
        # Busca nome do tutor
        tutor_dados = self.pet_controller.buscar_tutor_por_pet(id_pet)
        nome_tutor = (tutor_dados.get('nome_tutor') or 
                      tutor_dados.get('NOME') or 
                      'Não informado') if tutor_dados else 'Não informado'
        
        ctk.CTkLabel(tutor_box, text=nome_tutor, font=("Helvetica", 13, "bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=12, pady=(0, 8))

        # Peso e Sexo - Dados do banco
        peso = pet_dados.get('PESO', '? kg') if pet_dados else '? kg'
        sexo = pet_dados.get('SEXO', 'Não informado') if pet_dados else 'Não informado'
        
        if not isinstance(peso, str):
            peso = f"{peso} kg"
        elif peso and not peso.endswith('kg'):
            peso = f"{peso} kg"
        
        row_stats = ctk.CTkFrame(card_esq, fg_color="transparent")
        row_stats.pack(fill="x", padx=15, pady=15)
        
        p_box = ctk.CTkFrame(row_stats, fg_color=colors.STATUS_HEALTHY_BG, corner_radius=12, height=70) # Cor ajustada
        p_box.pack(side="left", fill="both", expand=True, padx=(0, 4))
        ctk.CTkLabel(p_box, text=tr("PESO"), font=("Helvetica", 9, "bold"), text_color=colors.STATUS_HEALTHY_TEXT).pack(pady=(8, 0))
        ctk.CTkLabel(p_box, text=str(peso), font=("Helvetica", 16, "bold"), text_color=colors.STATUS_HEALTHY_TEXT).pack(pady=(0, 5))

        s_box = ctk.CTkFrame(row_stats, fg_color=colors.NEUTRAL_100, corner_radius=12, height=70) # Cor ajustada
        s_box.pack(side="left", fill="both", expand=True, padx=(4, 0))
        ctk.CTkLabel(s_box, text=tr("SEXO"), font=("Helvetica", 9, "bold"), text_color=colors.TEXT_SECONDARY).pack(pady=(8, 0)) # Cor ajustada
        ctk.CTkLabel(s_box, text=str(sexo), font=("Helvetica", 16, "bold"), text_color=colors.TEXT_PRIMARY).pack(pady=(0, 5)) # Cor ajustada

        # Próxima consulta (assumindo que seja uma info dinâmica ou mockada)
        prox_c = ctk.CTkFrame(card_esq, fg_color=colors.ACCENT_GREEN, corner_radius=30) # Cor ajustada
        prox_c.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(prox_c, text=tr("Próxima consulta: 15 de Fev"), font=("Helvetica", 15, "bold"), text_color="white").pack(anchor="w", padx=15, pady=8)

        # Coluna direita responsiva
        self.right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=20, # Raio ajustado
                                     border_width=1, border_color=colors.NEUTRAL_200)
        if modo_vertical:
            self.right_col.grid(row=1, column=0, sticky="ew", padx=0)
        else:
            self.right_col.grid(row=0, column=1, sticky="nsew", padx=0)
        
        # Guardar dados do pet para uso em mudar_aba_pet
        self.dados_pet_atual = pet_dados

        # --- Trecho corrigido do Header das Abas ---
        tab_header = ctk.CTkFrame(self.right_col, fg_color=colors.GRAY_LIGHT, corner_radius=15, height=45) # Cor e raio ajustados
        tab_header.pack(pady=30, padx=30, anchor="w")
        tab_header.pack_propagate(False) # Garante que o height seja respeitado

        self.abas_botoes = {}
        abas = [
            (tr("SOBRE"), "sobre"),
            (tr("SAÚDE"), "saude"),
            (tr("MEDICAMENTOS"), "medicamentos"),
            (tr("EMOCIONAL"), "emocional")
        ]

        for nome, chave in abas:
            btn = ctk.CTkButton(
                tab_header, text=nome, width=110, corner_radius=10, # Raio menor
                fg_color="transparent", text_color=colors.TEXT_PRIMARY, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                command=lambda c=chave: self.mudar_aba_pet(c)
            )
            btn.pack(side="left", padx=2, pady=2)
            self.abas_botoes[chave] = btn

        self.container_abas = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.container_abas.pack(fill="both", expand=True, padx=40)

        self.mudar_aba_pet("sobre")

    # --- MÉTODOS DE RENDERIZAÇÃO DAS ABAS ---

    # --- ABA: SOBRE ---
    def _renderizar_aba_sobre(self):
        ctk.CTkLabel(self.container_abas, text=tr("Sobre o pet:"), font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", pady=(10, 5))
        
        # Pega a descrição da coluna DESCRICAO do seu banco
        desc_texto = self.dados_pet_atual.get('DESCRICAO') or tr("Sem descrição registrada.")
        ctk.CTkLabel(self.container_abas, text=desc_texto, font=ctk.CTkFont(family="Helvetica", size=14), text_color=colors.TEXT_SECONDARY, wraplength=600, justify="left").pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.container_abas, text=tr("Personalidade"), font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", pady=(0, 10))
        
        # Pega as tags da coluna PERSONALIDADE
        tags_raw = self.dados_pet_atual.get('PERSONALIDADE') or "Dócil, Agitado"
        tags = [t.strip() for t in tags_raw.split(',')]
        
        tags_frame = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        tags_frame.pack(anchor="w")

        for t in tags:
            tag = ctk.CTkFrame(tags_frame, fg_color="#F3F4F6", corner_radius=15) # Cor ajustada
            tag.pack(side="left", padx=5)
            ctk.CTkLabel(tag, text=t, font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"), text_color=colors.TEXT_PRIMARY).pack(padx=15, pady=5)

    # --- ABA: SAÚDE (Vacinas) ---
    def _renderizar_aba_saude(self):
        header = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text=tr("Protocolo de Vacinação"), font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"), text_color=colors.TEXT_DARK).pack(side="left")
        ctk.CTkButton(
            header, 
            text=tr("+ NOVO REGISTRO"), 
            fg_color=colors.ACCENT_GREEN, 
            hover_color=colors.ACCENT_GREEN_HOVER,
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), 
            height=35, 
            corner_radius=8, 
            command=self.abrir_modal_nova_vacina
        ).pack(side="right")
        
        vacinas = self.pet_controller.buscar_vacinas_por_pet(self.pet_atual_id)
        if not vacinas:
            ctk.CTkLabel(self.container_abas, text=tr("Sem vacinas."), text_color=colors.NEUTRAL_500).pack(pady=20)
        else:
            for v in vacinas:
                card = ctk.CTkFrame(self.container_abas, fg_color="white", corner_radius=15, border_width=1, border_color=colors.NEUTRAL_200)
                card.pack(fill="x", pady=8)
                txt = f"{v.get('NOME')}\n{tr('Próxima dose')}: {v.get('PROXIMA_DOSE')}"
                ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=colors.TEXT_PRIMARY, justify="left").pack(anchor="w", padx=15, pady=12)

    def _carregar_foto_pet_perfil(self, id_pet):
        """Carrega a foto do pet do S3 para a tela de perfil"""
        try:
            pet = self.pet_controller.buscar_pet(id_pet)
            if not pet:
                print(f"Pet com ID {id_pet} não encontrado")
                return
            
            imagem_key = pet.get("IMAGEM")
            
            if imagem_key and str(imagem_key).strip():
                try:
                    url = get_url_s3(imagem_key, expires_in=604800)
                    if url:
                        session = requests.Session()
                        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
                        session.mount('https://', HTTPAdapter(max_retries=retries))
                        response = session.get(url, timeout=30)
                        response.raise_for_status()
                        
                        pil_img = Image.open(BytesIO(response.content))
                        pil_img = pil_img.resize((200, 200), Image.Resampling.LANCZOS) # Tamanho ajustado para perfil
                        
                        ctk_img = ctk.CTkImage(light_image=pil_img, size=(200, 200))
                        
                        self.img_label.destroy()
                        self.img_label = ctk.CTkLabel(
                            self.img_placeholder,
                            image=ctk_img,
                            text="",
                            fg_color=colors.NEUTRAL_100 # Cor de fundo consistente
                        )
                        self.img_label.image = ctk_img
                        self.img_label.pack(fill="both", expand=True)
                except Exception as e:
                    print(f"Erro ao carregar foto do S3 para perfil: {e}")
            else:
                self.img_label.configure(text="🐾", font=("Arial", 80), image=None, text_color=colors.NEUTRAL_500) # Volta para emoji se não tiver imagem
        except Exception as e:
            print(f"Erro ao verificar imagem do pet para perfil: {e}")

    def escolher_foto_pet(self):
        file_path = filedialog.askopenfilename(
            title="Selecione uma foto para o pet",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos", "*.*")]
        )
        if file_path:
            self._fazer_upload_foto_pet(file_path)

    def _fazer_upload_foto_pet(self, file_path):
        try:
            imagem_key = upload_foto_pet_s3(file_path, self.pet_atual_id)
            
            if not imagem_key:
                messagebox.showerror(tr("Erro"), tr("Falha ao fazer upload da foto"))
                return
            
            sucesso = self.pet_controller.atualizar_imagem_pet(self.pet_atual_id, imagem_key)
            
            if sucesso:
                try:
                    pil_img = Image.open(file_path)
                    pil_img = pil_img.resize((200, 200), Image.Resampling.LANCZOS)
                    
                    ctk_img = ctk.CTkImage(light_image=pil_img, size=(200, 200))
                    
                    self.img_label.destroy()
                    self.img_label = ctk.CTkLabel(
                        self.img_placeholder,
                        image=ctk_img,
                        text="",
                        fg_color=colors.NEUTRAL_100
                    )
                    self.img_label.image = ctk_img
                    self.img_label.pack(fill="both", expand=True)
                    
                    messagebox.showinfo(tr("Sucesso"), tr("Foto do pet atualizada com sucesso!"))
                except Exception as e:
                    print(f"Erro ao exibir foto: {e}")
                    messagebox.showwarning(tr("Aviso"), tr("Foto salva no banco mas não foi possível exibir"))
            else:
                messagebox.showerror(tr("Erro"), tr("Falha ao atualizar foto no banco de dados"))
        except Exception as e:
            print(f"Erro ao fazer upload: {e}")
            messagebox.showerror(tr("Erro"), f"{tr('Erro ao processar foto')}: {str(e)}")

    def mudar_aba_pet(self, aba):
        self.active_aba = aba
        
        for chave, btn in self.abas_botoes.items():
            if chave == aba:
                btn.configure(fg_color=colors.ACCENT_GREEN, text_color="white") # Cor da aba ativa
            else:
                btn.configure(fg_color="transparent", text_color=colors.TEXT_PRIMARY)

        for w in self.container_abas.winfo_children():
            w.destroy()

        if aba == "sobre":
            self._renderizar_aba_sobre()
        elif aba == "saude":
            self._renderizar_aba_saude()
        elif aba == "medicamentos":
            self._renderizar_aba_medicamentos()
        elif aba == "emocional":
            self._renderizar_aba_emocional()
            
    def _renderizar_aba_medicamentos(self):
        header = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text=tr("Medicamentos em Uso"),
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text=tr("+ NOVO MEDICAMENTO"),
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            height=35,
            corner_radius=8,
            command=self.abrir_modal_novo_medicamento
        ).pack(side="right")

        list_frame = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        list_frame.pack(fill="both", expand=True)

        medicamentos = self.pet_controller.buscar_medicamentos_por_pet(self.pet_atual_id)
        # Simula medicamentos para teste se o controller retornar vazio
        if not medicamentos:
             medicamentos = [
                {'NOME': 'Antibiótico A', 'DOSAGEM': '50mg', 'HORARIO': '8h, 20h', 'DATA_INICIO': '2024-01-01', 'DATA_FIM': '2024-01-10', 'OBSERVACOES': 'Tomar com comida.'},
                {'NOME': 'Anti-inflamatório B', 'DOSAGEM': '10mg', 'HORARIO': '12h', 'DATA_INICIO': '2024-01-05', 'DATA_FIM': '2024-01-12', 'OBSERVACOES': 'Pode causar sonolência.'},
             ]


        if not medicamentos:
            empty_card = ctk.CTkFrame(
                list_frame,
                fg_color="transparent",
                border_width=1,
                border_color=colors.NEUTRAL_200,
                corner_radius=15,
                height=100
            )
            empty_card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                empty_card,
                text=tr("Nenhum medicamento registrado."),
                font=ctk.CTkFont(family="Helvetica", size=12, weight="italic"),
                text_color=colors.NEUTRAL_500
            ).place(relx=0.5, rely=0.5, anchor="center")

        else:
            for med in medicamentos:
                card = ctk.CTkFrame(
                    list_frame,
                    fg_color="white",
                    corner_radius=12,
                    border_width=1,
                    border_color=colors.NEUTRAL_200
                )
                card.pack(fill="x", pady=8)

                nome = med.get("NOME", "")
                horario = med.get("HORARIO", "")
                inicio = med.get("DATA_INICIO", "")
                fim = med.get("DATA_FIM", "")
                obs = med.get("OBSERVACOES", "")

                texto = f"💊 {nome}\n⏰ {horario} | 📅 {inicio} até {fim}\n📝 {obs}"

                ctk.CTkLabel(
                    card,
                    text=texto,
                    justify="left",
                    font=ctk.CTkFont(family="Helvetica", size=12),
                    text_color=colors.TEXT_PRIMARY
                ).pack(anchor="w", padx=15, pady=12)

    def _renderizar_aba_emocional(self):
        historico = self.pet_controller.buscar_historico_emocional(self.pet_atual_id)
        
        if not historico:
            historico = [ # Dados de simulação
                {'data': '2024-01-01', 'nivel': 2, 'nota': 'Comportamento normal.'},
                {'data': '2024-01-08', 'nivel': 3, 'nota': 'Muito brincalhão esta semana!'},
                {'data': '2024-01-15', 'nivel': 2, 'nota': 'Um pouco mais calmo.'},
                {'data': '2024-01-22', 'nivel': 1, 'nota': 'Parece triste, comeu menos.'},
                {'data': '2024-01-29', 'nivel': 2, 'nota': 'Melhorando, voltou a brincar um pouco.'},
                {'data': '2024-02-05', 'nivel': 3, 'nota': 'Cheio de energia!'}
            ]

        if not historico: # Caso ainda não haja dados mesmo com a simulação
            datas = []
            niveis = []
            status_humor = "Não registrado"
            emoji_humor = "❓"
            nota_tutor = "Nenhuma nota registrada."
        else:
            datas = [
                datetime.strptime(h.get('data', ''), "%Y-%m-%d").strftime("%d/%m")
                for h in historico
            ]
            niveis = [h.get('nivel', 0) for h in historico]
            
            ultimo = historico[-1]
            nota_tutor = ultimo.get('nota', 'Sem observações')
            nivel_atual = ultimo.get('nivel', 0)
            
            mapping = {3: ("Muito Feliz", "😊"), 2: ("Estável", "😐"), 1: ("Amuado", "😔")}
            status_humor, emoji_humor = mapping.get(nivel_atual, ("Indefinido", "😶"))

        main_row = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        main_row.pack(fill="both", expand=True)

        chart_container = ctk.CTkFrame(main_row, fg_color="white", corner_radius=20, border_width=1, border_color=colors.NEUTRAL_200)
        chart_container.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(chart_container, text=tr("Bem-estar do Pet"), font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), text_color=colors.TEXT_DARK).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(chart_container, text=tr("TENDÊNCIA SEMANAL"), font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"), text_color=colors.NEUTRAL_500).pack(anchor="w", padx=20)

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('white')
        
        ax.plot(datas, niveis, color=colors.ACCENT_GREEN, marker='o', linewidth=3, markersize=8)
        ax.fill_between(datas, niveis, color=colors.ACCENT_GREEN, alpha=0.1)
        
        ax.set_ylim(0, 4)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["😔", "😐", "😊"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        right_panel = ctk.CTkFrame(main_row, fg_color="transparent", width=250)
        right_panel.pack(side="left", fill="y")

        humor_card = ctk.CTkFrame(right_panel, fg_color=colors.ACCENT_GREEN, corner_radius=20)
        humor_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(humor_card, text=tr("HUMOR REGISTRADO"), font=ctk.CTkFont(family="Helvetica", size=9, weight="bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(humor_card, text=emoji_humor, font=("Arial", 40)).pack()
        ctk.CTkLabel(humor_card, text=status_humor, font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), text_color="white").pack(pady=(5, 15))

        nota_card = ctk.CTkFrame(right_panel, fg_color=colors.NEUTRAL_100, corner_radius=15) # Cor ajustada
        nota_card.pack(fill="x")
        ctk.CTkLabel(nota_card, text=f"💬 {tr('NOTA DO TUTOR')}", font=ctk.CTkFont(family="Helvetica", size=9, weight="bold"), text_color=colors.NEUTRAL_500).pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(nota_card, text=f'"{nota_tutor}"', font=ctk.CTkFont(family="Helvetica", size=12, weight="italic"), text_color=colors.TEXT_SECONDARY, wraplength=200).pack(anchor="w", padx=15, pady=(5, 15))
        
    def abrir_modal_novo_medicamento(self):
        self.overlay_med = ctk.CTkFrame(self.content.master, fg_color="black") # Cor preta para o overlay
        self.overlay_med.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay_med,
            width=500,
            height=600,
            corner_radius=30,
            fg_color="white" # Fundo branco
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(
            modal,
            text=tr("Novo Medicamento"),
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=colors.TEXT_DARK
        ).pack(pady=(30, 20))

        def criar_input(placeholder):
            entry = ctk.CTkEntry(
                modal,
                placeholder_text=placeholder,
                height=50,
                corner_radius=15, # Raio ajustado
                border_width=1, # Borda sutil
                fg_color=colors.GRAY_LIGHT, # Fundo do input
                text_color=colors.TEXT_PRIMARY,
                placeholder_text_color=colors.NEUTRAL_500,
                font=ctk.CTkFont(family="Helvetica", size=14)
            )
            entry.pack(fill="x", padx=50, pady=10)
            return entry

        self.ent_med_nome = criar_input(tr("Nome do Medicamento"))
        self.ent_med_dose = criar_input(tr("Dosagem (ex: 50mg)"))
        self.ent_med_freq = criar_input(tr("Frequência (ex: 2x ao dia)"))

        self.ent_med_inicio = criar_input(tr("Data de Início (DD/MM/AAAA)")) # Placeholder ajustado
        self.ent_med_fim = criar_input(tr("Data de Término (DD/MM/AAAA)")) # Placeholder ajustado

        btn_box = ctk.CTkFrame(modal, fg_color="transparent")
        btn_box.pack(fill="x", padx=50, pady=30)
        btn_box.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(
            btn_box,
            text=tr("Cancelar"),
            fg_color=colors.NEUTRAL_200,
            hover_color=colors.NEUTRAL_300,
            text_color=colors.TEXT_PRIMARY,
            height=50,
            corner_radius=15, # Raio ajustado
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=lambda: self.overlay_med.destroy()
        ).grid(row=0, column=0, padx=10, sticky="ew")

        ctk.CTkButton(
            btn_box,
            text=tr("Adicionar à Lista"),
            fg_color=colors.ACCENT_GREEN,
            hover_color=colors.ACCENT_GREEN_HOVER,
            height=50,
            corner_radius=15, # Raio ajustado
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=self.salvar_novo_medicamento
        ).grid(row=0, column=1, padx=10, sticky="ew")

    def salvar_novo_medicamento(self):
        nome = self.ent_med_nome.get().strip()
        dose = self.ent_med_dose.get().strip()
        freq = self.ent_med_freq.get().strip()
        inicio = self.ent_med_inicio.get().strip()
        fim = self.ent_med_fim.get().strip()

        if not nome:
            messagebox.showwarning(tr("Aviso"), tr("Digite o nome do medicamento"))
            return

        def converter_data(data):
            if not data:
                return None
            try:
                return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                return "ERRO"

        inicio_formatado = converter_data(inicio)
        fim_formatado = converter_data(fim)

        if inicio_formatado == "ERRO" or fim_formatado == "ERRO":
            messagebox.showerror(tr("Erro"), tr("Use o formato DD/MM/AAAA para as datas"))
            return

        sucesso = self.pet_controller.adicionar_medicamento(
            self.pet_atual_id,
            nome,
            dose,
            freq,
            inicio_formatado,
            fim_formatado
        )

        if sucesso:
            messagebox.showinfo(tr("Sucesso"), tr("Medicamento adicionado!"))
            self.overlay_med.destroy()
            self.mudar_aba_pet("medicamentos")
        else:
            messagebox.showerror(tr("Erro"), tr("Não foi possível salvar."))

    def abrir_modal_nova_vacina(self):
        self.overlay_vacina = ctk.CTkFrame(self.content.master, fg_color="black") # Cor preta para o overlay
        self.overlay_vacina.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.modal_vacina = ctk.CTkFrame(
            self.overlay_vacina, 
            width=420,
            corner_radius=20, 
            border_width=0, # Sem borda
            fg_color="white"
        )
        self.modal_vacina.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.modal_vacina, 
            text="💉", 
            font=("Arial", 40),
            text_color=colors.ACCENT_GREEN # Cor ajustada
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.modal_vacina, 
            text=tr("Novo Registro"), 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"), 
            text_color=colors.TEXT_DARK
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            self.modal_vacina, 
            text=tr("Insira os dados da aplicação abaixo."), 
            font=ctk.CTkFont(family="Helvetica", size=12), 
            text_color=colors.TEXT_SECONDARY
        ).pack(pady=(0, 20))

        form = ctk.CTkFrame(self.modal_vacina, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        ctk.CTkLabel(form, text=tr("Nome da Vacina"), font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=colors.TEXT_PRIMARY).pack(anchor="w", pady=(10, 0))
        self.entry_nome_vacina = ctk.CTkEntry(
            form, 
            height=45, 
            corner_radius=10, 
            border_color=colors.NEUTRAL_200, 
            fg_color=colors.GRAY_LIGHT,
            text_color=colors.TEXT_PRIMARY,
            placeholder_text_color=colors.NEUTRAL_500,
            border_width=1,
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.entry_nome_vacina.pack(fill="x", pady=(2, 15))

        ctk.CTkLabel(form, text=tr("Data de Aplicação"), font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 0))
        self.entry_data_aplicacao = ctk.CTkEntry(
            form, 
            placeholder_text="DD/MM/AAAA", 
            height=45, 
            corner_radius=10, 
            border_color=colors.NEUTRAL_200, 
            fg_color=colors.GRAY_LIGHT,
            text_color=colors.TEXT_PRIMARY,
            placeholder_text_color=colors.NEUTRAL_500,
            border_width=1,
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.entry_data_aplicacao.pack(fill="x", pady=(2, 15))

        ctk.CTkLabel(form, text=tr("Próxima Dose"), font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 0))
        self.entry_proxima_dose = ctk.CTkEntry(
            form, 
            placeholder_text="DD/MM/AAAA", 
            height=45, 
            corner_radius=10, 
            border_color=colors.NEUTRAL_200, 
            fg_color=colors.GRAY_LIGHT,
            text_color=colors.TEXT_PRIMARY,
            placeholder_text_color=colors.NEUTRAL_500,
            border_width=1,
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.entry_proxima_dose.pack(fill="x", pady=(2, 20))

        btn_container = ctk.CTkFrame(self.modal_vacina, fg_color="transparent")
        btn_container.pack(fill="x", pady=20, padx=30)

        btn_container.columnconfigure((0, 1), weight=1)

        btn_cancelar = ctk.CTkButton(
            btn_container, 
            text=tr("CANCELAR"), 
            fg_color=colors.NEUTRAL_200, 
            text_color=colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            height=50,
            corner_radius=10,
            command=self.fechar_modal_vacina
        )
        btn_cancelar.grid(row=0, column=0, padx=6, sticky="ew")

        btn_salvar = ctk.CTkButton(
            btn_container, 
            text=tr("SALVAR REGISTRO"), 
            fg_color=colors.ACCENT_GREEN, 
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            height=50,
            corner_radius=10,
            command=self.salvar_nova_vacina
        )
        btn_salvar.grid(row=0, column=1, padx=6, sticky="ew")


    def fechar_modal_vacina(self):
        if hasattr(self, 'overlay_vacina') and self.overlay_vacina:
            self.overlay_vacina.destroy()

    def salvar_nova_vacina(self):
        from datetime import datetime
        
        nome_vacina = self.entry_nome_vacina.get().strip()
        data_aplicacao = self.entry_data_aplicacao.get().strip() # Adicionado para uso futuro, não salvo ainda
        proxima_dose = self.entry_proxima_dose.get().strip()

        if not nome_vacina:
            messagebox.showwarning(tr("Aviso"), tr("Por favor, insira o nome da vacina"))
            return
        if not data_aplicacao: # Adicionada validação para data_aplicacao
            messagebox.showwarning(tr("Aviso"), tr("Por favor, insira a data de aplicação"))
            return
        if not proxima_dose:
            messagebox.showwarning(tr("Aviso"), tr("Por favor, insira a data da próxima dose"))
            return

        try:
            # Validar e formatar data de aplicação e próxima dose
            data_aplicacao_obj = datetime.strptime(data_aplicacao, "%d/%m/%Y")
            proxima_dose_obj = datetime.strptime(proxima_dose, "%d/%m/%Y")
            
            data_aplicacao_formatada = data_aplicacao_obj.strftime("%Y-%m-%d")
            proxima_dose_formatada = proxima_dose_obj.strftime("%Y-%m-%d")

        except ValueError:
            messagebox.showerror(tr("Erro"), tr("Data inválida! Use o formato DD/MM/YYYY"))
            return

        sucesso = self.pet_controller.adicionar_vacina(
            self.pet_atual_id, 
            nome_vacina, 
            proxima_dose_formatada # Assumindo que seu método de adicionar vacina já recebe isso
        )

        if sucesso:
            messagebox.showinfo(tr("Sucesso"), tr("Vacina registrada com sucesso!"))
            self.fechar_modal_vacina()
            self.mudar_aba_pet("saude")
        else:
            messagebox.showerror(tr("Erro"), tr("Falha ao registrar a vacina"))

    def _carregar_foto_card(self, label, imagem_key):
        """Carrega foto do S3 para exibir no card de pacientes"""
        try:
            if not imagem_key or not str(imagem_key).strip():
                # Usa a imagem padrão se não houver key ou estiver vazia
                if self.default_pet_image:
                    label.configure(image=self.default_pet_image, text="")
                    label.img_ref = self.default_pet_image
                else:
                    label.configure(text="🐾", font=("Arial", 60), text_color=colors.NEUTRAL_500)
                return
            
            url = get_url_s3(imagem_key, expires_in=604800)
            
            if url:
                session = requests.Session()
                retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
                session.mount('https://', HTTPAdapter(max_retries=retries))
                
                response = session.get(url, timeout=10) # Reduzido timeout para cards
                if response.status_code == 404:
                    print(f"Foto do pet nÃ£o encontrada no S3: {imagem_key}")
                    self._usar_imagem_padrao(label)
                    return

                response.raise_for_status()
                
                pil_img = Image.open(BytesIO(response.content))
                # Redimensionar para caber no card (180x120 como na imagem)
                pil_img = pil_img.resize((180, 120), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(180, 120))
                
                label.configure(image=ctk_img, text="")
                label.img_ref = ctk_img
            else:
                # Fallback para imagem padrão se a URL não for gerada
                if self.default_pet_image:
                    label.configure(image=self.default_pet_image, text="")
                    label.img_ref = self.default_pet_image
                else:
                    label.configure(text="🐾", font=("Arial", 60), text_color=colors.NEUTRAL_500)
        except Exception as e:
            print(f"Erro ao carregar foto no card: {e}")
            # Fallback para imagem padrão em caso de erro no download/processamento
            if self.default_pet_image:
                label.configure(image=self.default_pet_image, text="")
                label.img_ref = self.default_pet_image
            else:
                label.configure(text="🐾", font=("Arial", 60), text_color=colors.NEUTRAL_500)
