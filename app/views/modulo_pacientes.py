import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image
from io import BytesIO
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np # opcional para gerar dados do gráfico
from app.controllers.pet_controller import PetController
from app.services.s3_client import upload_foto_pet_s3, get_url_s3
import uuid

class ModuloPacientes:
    def __init__(self, content_frame, pet_controller: PetController):
        self.content = content_frame
        self.pet_controller = pet_controller

    def tela_pacientes(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # Cabeçalho
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold")).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Novo Paciente",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            width=150,
            corner_radius=10,
            command=self.abrir_popup_novo_paciente
        ).pack(side="right")

        # Campo de busca
        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 30))
        ctk.CTkEntry(
            search_row,
            placeholder_text="🔍 Pesquise por tutor ou pet",
            height=45,
            corner_radius=22
        ).pack(side="left", fill="x", expand=True, padx=(0, 15))

        # Grid de cards
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)
        grid.rowconfigure((0, 1, 2), weight=1)

        # Busca os pets reais do banco
        pets = self.pet_controller.listar_pets()

        for i, pet in enumerate(pets):
            # CHAVES CORRETAS do seu banco (conforme o print)
            id_pet = pet.get('id')
            nome = pet.get('NOME', 'Sem nome')
            especie   = pet.get('ESPECIE', '').lower()
            raca      = pet.get('RACA', 'Sem raça')
            data_nasc = pet.get('DATA_NASCIMENTO')
            sexo      = pet.get('SEXO', 'Não informado')
            castrado  = pet.get('CASTRADO', 'Não informado')
            peso      = pet.get('PESO') or '? kg'            # evita None
            imagem_key = pet.get('IMAGEM')  # Nova: pega a chave da imagem

            idade     = self.calcular_idade(data_nasc)
            emoji     = "🐶" if "cachorro" in especie else "🐱" if "gato" in especie else "🐾"
            info      = f"{raca} • {idade} anos • {sexo}"

            # Cria o card e OBTÉM o frame retornado
            card = self.criar_card_paciente(
                grid,
                nome,
                info,
                emoji,
                peso,
                i // 3,   # linha
                i % 3,     # coluna
                id_pet,
                raca,
                imagem_key  # Novo: passa a chave da imagem
            )

            # Tornar o card clicável sem sobrepor widgets — liga evento de clique ao frame
            def _abrir_perfil(event=None, pid=id_pet, n=nome, r=raca, e_emoji=emoji):
                self.tela_perfil_pet(pid, n, r, e_emoji)

            card.bind("<Button-1>", _abrir_perfil)
            # opcional: mudar cursor ao passar o mouse
            try:
                card.configure(cursor="hand2")
            except Exception:
                pass

    def calcular_idade(self, data_nasc):
        """Calcula idade em anos a partir da data de nascimento"""
        if not data_nasc:
            return "?"
        try:
            if isinstance(data_nasc, str):
                data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d")
            elif not isinstance(data_nasc, datetime):
                return "?"
            hoje = datetime.now()
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            return str(idade)
        except Exception:
            return "?"

    def criar_card_paciente(self, master, nome, info, icon, peso, row, col, id_pet, raca, imagem_key=None):
        """Card com botão para ver perfil"""
        card = ctk.CTkFrame(
            master,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # Força tamanho fixo (importante!)
        card.grid_propagate(False)
        card.configure(width=320, height=420)

        # Configura grid interno do card
        card.columnconfigure(0, weight=1)
        card.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Container para imagem/emoji
        img_frame = ctk.CTkFrame(card, fg_color="transparent")
        img_frame.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")

        # Label para emoji ou imagem
        emoji_lbl = ctk.CTkLabel(
            img_frame,
            text=icon,
            font=("Arial", 80)
        )
        emoji_lbl.pack(fill="both", expand=True)

        # Tentar carregar foto do S3 se existir (com delay para renderização)
        if imagem_key and str(imagem_key).strip():
            card.after(300, lambda: self._carregar_foto_card(emoji_lbl, imagem_key))

        # Nome
        nome_lbl = ctk.CTkLabel(
            card,
            text=nome,
            font=("Arial", 20, "bold"),
            text_color="#000000"
        )
        nome_lbl.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")

        # Info
        info_lbl = ctk.CTkLabel(
            card,
            text=info,
            font=("Arial", 14),
            text_color="#64748B"
        )
        info_lbl.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

        # Peso
        peso_lbl = ctk.CTkLabel(
            card,
            text=f"Peso: {peso}",
            font=("Arial", 13),
            text_color="#94A3B8"
        )
        peso_lbl.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        # Botão Ver Perfil
        def abrir_perfil():
            self.tela_perfil_pet(id_pet, nome, raca, icon)

        btn_perfil = ctk.CTkButton(
            card,
            text="👁️ Ver Perfil",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            text_color="white",
            font=("Arial", 13, "bold"),
            corner_radius=10,
            height=40,
            command=abrir_perfil
        )
        btn_perfil.grid(row=4, column=0, columnspan=3, pady=15, padx=15, sticky="ew")

        return card
        

    def abrir_popup_novo_paciente(self):
        self.overlay = ctk.CTkFrame(self.content.master, fg_color="#1A1A1A") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.modal_frame = ctk.CTkFrame(self.overlay, width=400, height=520, corner_radius=20, 
                                       border_width=2, border_color="#14B8A6", fg_color="white")
        self.modal_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.modal_frame.pack_propagate(False)

        ctk.CTkLabel(self.modal_frame, text="🐾 Novo Paciente", font=("Arial", 22, "bold"), 
                     text_color="#14B8A6").pack(pady=20)

        form = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        def criar_input(label):
            ctk.CTkLabel(form, text=label, font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1")
            entry.pack(fill="x", pady=(2, 5))
            return entry

        criar_input("Nome do Pet")
        criar_input("Nome do Tutor")
        criar_input("Telefone de Contato")
        
        ctk.CTkLabel(form, text="Observações Iniciais", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1").pack(fill="x", pady=(2, 5))

        btn_container = ctk.CTkFrame(self.modal_frame, fg_color="transparent")
        btn_container.pack(fill="x", pady=25, padx=30)

        ctk.CTkButton(btn_container, text="Confirmar", fg_color="#14B8A6", width=160, height=40,
                      command=self.fechar_popup).pack(side="left", padx=5)
        ctk.CTkButton(btn_container, text="Cancelar", fg_color="#94A3B8", width=160, height=40,
                      command=self.fechar_popup).pack(side="right", padx=5)

    def fechar_popup(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()

    def tela_perfil_pet(self, id_pet, nome_pet, raca_pet, emoji):
        # Guardar id do pet para usar nas funções de atualizar foto
        self.pet_atual_id = id_pet
        
        # Buscar dados completos do pet no banco
        pet_dados = self.pet_controller.buscar_pet(id_pet)
        
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
            card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, 
                                   border_width=1, border_color="#F1F5F9")
            card_esq.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))
        else:
            card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, 
                                   width=350, border_width=1, border_color="#F1F5F9")
            card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Container para imagem com botão de mudar
        img_container = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", height=220, corner_radius=30)
        img_container.pack(fill="x", padx=20, pady=20)
        img_container.pack_propagate(False)
        
        # Frame para a imagem
        self.img_placeholder = ctk.CTkFrame(img_container, fg_color="#F8FAFC")
        self.img_placeholder.pack(fill="both", expand=True)
        
        # Label da imagem/emoji
        self.img_label = ctk.CTkLabel(
            self.img_placeholder, 
            text=emoji, 
            font=("Arial", 80),
            fg_color="#F8FAFC"
        )
        self.img_label.pack(fill="both", expand=True)
        
        # Tentar carregar foto do S3 se existir (com delay para garantir renderização)
        self.content.after(500, lambda: self._carregar_foto_pet(id_pet, emoji))
        
        # Botão para mudar foto (overlay)
        btn_mudar = ctk.CTkButton(
            img_container,
            text="📷 Mudar Foto",
            font=("Arial", 12, "bold"),
            text_color="white",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            height=35,
            corner_radius=10,
            command=self.escolher_foto_pet
        )
        btn_mudar.place(relx=0.5, rely=0.9, anchor="center")

        ctk.CTkLabel(card_esq, text=nome_pet, font=("Arial", 28, "bold"), text_color="#1E293B").pack(pady=(5, 0))
        ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Arial", 11, "bold"), text_color="#14B8A6").pack(pady=(2, 15))
        
        ctk.CTkLabel(card_esq, text=f"ID: {id_pet}", font=("Arial", 10), text_color="#94A3B8").pack(pady=(0, 8))

        # Tutor box
        tutor_box = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", corner_radius=15)
        tutor_box.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(tutor_box, text="TUTOR RESPONSÁVEL", font=("Arial", 9, "bold"), text_color="#94A3B8").pack(anchor="w", padx=12, pady=(8, 0))
        
        # Busca nome do tutor
        tutor_dados = self.pet_controller.buscar_tutor_por_pet(id_pet)
        # Tenta encontrar o campo de nome em diferentes formatos
        nome_tutor = (tutor_dados.get('nome_tutor') or 
                      tutor_dados.get('NOME') or 
                      tutor_dados.get('nome') or 
                      tutor_dados.get('Name') or 
                      'Não informado') if tutor_dados else 'Não informado'
        
        ctk.CTkLabel(tutor_box, text=nome_tutor, font=("Arial", 13, "bold"), text_color="#1E293B").pack(anchor="w", padx=12, pady=(0, 8))

        # Peso e Sexo - Dados do banco
        peso = pet_dados.get('PESO', '? kg') if pet_dados else '? kg'
        sexo = pet_dados.get('SEXO', 'Não informado') if pet_dados else 'Não informado'
        
        if not isinstance(peso, str):
            peso = f"{peso} kg"
        elif peso and not peso.endswith('kg'):
            peso = f"{peso} kg"
        
        row_stats = ctk.CTkFrame(card_esq, fg_color="transparent")
        row_stats.pack(fill="x", padx=15, pady=15)
        
        p_box = ctk.CTkFrame(row_stats, fg_color="#F0FDFA", corner_radius=12, height=70)
        p_box.pack(side="left", fill="both", expand=True, padx=(0, 4))
        ctk.CTkLabel(p_box, text="PESO", font=("Arial", 9, "bold"), text_color="#134E4A").pack(pady=(8, 0))
        ctk.CTkLabel(p_box, text=str(peso), font=("Arial", 16, "bold"), text_color="#134E4A").pack(pady=(0, 5))

        s_box = ctk.CTkFrame(row_stats, fg_color="#EFF6FF", corner_radius=12, height=70)
        s_box.pack(side="left", fill="both", expand=True, padx=(4, 0))
        ctk.CTkLabel(s_box, text="SEXO", font=("Arial", 9, "bold"), text_color="#1E3A8A").pack(pady=(8, 0))
        ctk.CTkLabel(s_box, text=str(sexo), font=("Arial", 16, "bold"), text_color="#1E3A8A").pack(pady=(0, 5))

        prox_c = ctk.CTkFrame(card_esq, fg_color="#14B8A6", corner_radius=30)
        prox_c.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(prox_c, text="próxima consulta: 15 de Fev", font=("Arial", 15, "bold"), text_color="white").pack(anchor="w", padx=15, pady=8)

        # Coluna direita responsiva
        self.right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=40, 
                                     border_width=1, border_color="#F1F5F9")
        if modo_vertical:
            self.right_col.grid(row=1, column=0, sticky="ew", padx=0)
        else:
            self.right_col.grid(row=0, column=1, sticky="nsew", padx=0)
        
        # Guardar dados do pet para uso em mudar_aba_pet
        self.dados_pet_atual = pet_dados

        # --- Trecho corrigido do Header das Abas ---
        tab_header = ctk.CTkFrame(self.right_col, fg_color="#F1F5F9", corner_radius=25, height=50)
        tab_header.pack(pady=30, padx=30, anchor="w")

        self.abas_botoes = {}
        abas = [
            ("SOBRE", "sobre"),
            ("SAÚDE", "saude"),
            ("MEDICAMENTOS", "medicamentos"),
            ("EMOCIONAL", "emocional")
        ]

        for nome, chave in abas:
            btn = ctk.CTkButton(
                tab_header, text=nome, width=110, corner_radius=25,
                fg_color="transparent", text_color="#1E293B", font=("Arial", 11, "bold"),
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
        ctk.CTkLabel(self.container_abas, text="Sobre o pet:", font=("Arial", 18, "bold"), text_color="#1E293B").pack(anchor="w", pady=(10, 5))
        
        # Pega a descrição da coluna DESCRICAO do seu banco
        desc_texto = self.dados_pet_atual.get('DESCRICAO') or "Sem descrição registrada."
        ctk.CTkLabel(self.container_abas, text=desc_texto, font=("Arial", 14), text_color="#334155", wraplength=600, justify="left").pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.container_abas, text="Personalidade", font=("Arial", 16, "bold"), text_color="#1E293B").pack(anchor="w", pady=(0, 10))
        
        # Pega as tags da coluna PERSONALIDADE
        tags_raw = self.dados_pet_atual.get('PERSONALIDADE') or "Dócil, Agitado"
        tags = [t.strip() for t in tags_raw.split(',')]
        
        tags_frame = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        tags_frame.pack(anchor="w")

        for t in tags:
            tag = ctk.CTkFrame(tags_frame, fg_color="#FEF3C7", corner_radius=20)
            tag.pack(side="left", padx=5)
            ctk.CTkLabel(tag, text=t, font=("Arial", 12, "bold"), text_color="#92400E").pack(padx=15, pady=5)

    # --- ABA: SAÚDE (Vacinas) ---
    def _renderizar_aba_saude(self):
        header = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Protocolo de Vacinação", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(header, text="+ NOVO REGISTRO", fg_color="#14B8A6", font=("Arial", 11, "bold"), height=35, corner_radius=8, command=self.abrir_modal_nova_vacina).pack(side="right")
        
        vacinas = self.pet_controller.buscar_vacinas_por_pet(self.pet_atual_id)
        if not vacinas:
            ctk.CTkLabel(self.container_abas, text="Sem vacinas.", text_color="#94A3B8").pack(pady=20)
        else:
            for v in vacinas:
                card = ctk.CTkFrame(self.container_abas, fg_color="white", corner_radius=15, border_width=1, border_color="#F1F5F9")
                card.pack(fill="x", pady=8)
                txt = f"{v.get('NOME')}\nPróxima dose: {v.get('PROXIMA_DOSE')}"
                ctk.CTkLabel(card, text=txt, font=("Arial", 11, "bold"), justify="left").pack(anchor="w", padx=15, pady=12)

    
        meds = self.pet_controller.buscar_medicamentos_por_pet(self.pet_atual_id)
        
        if not meds:
            empty = ctk.CTkFrame(self.container_abas, fg_color="transparent", border_width=1, border_color="#F1F5F9", corner_radius=15, height=80)
            empty.pack(fill="x", pady=10)
            ctk.CTkLabel(empty, text="Nenhum medicamento registrado.", font=("Arial", 12, "italic"), text_color="#94A3B8").place(relx=0.5, rely=0.5, anchor="center")
        else:
            for m in meds:
                card = ctk.CTkFrame(self.container_abas, fg_color="white", corner_radius=12, border_width=1, border_color="#F1F5F9")
                card.pack(fill="x", pady=5)
                # Ajuste os nomes das chaves ('NOME', 'DOSAGEM') conforme seu banco
                txt = f"💊 {m.get('NOME', 'Sem nome')} - {m.get('DOSAGEM', '')} ({m.get('HORARIO', m.get('FREQUENCIA', ''))})"
                ctk.CTkLabel(card, text=txt, font=("Arial", 12, "bold")).pack(side="left", padx=15, pady=10)

    
        
    # ... (Mantenha aqui as funções _renderizar_aba_medicamentos e _renderizar_aba_emocional que te mandei antes)
    def _carregar_foto_pet(self, id_pet, emoji_padrao):
        """Carrega a foto do pet do S3 se existir"""
        try:
            pet = self.pet_controller.buscar_pet(id_pet)
            
            if not pet:
                print(f"Pet com ID {id_pet} não encontrado")
                return
            
            imagem_key = pet.get("IMAGEM")
            print(f"Buscando imagem para pet {id_pet}: chave = {imagem_key}")
            
            if imagem_key and str(imagem_key).strip():  # Verifica se não é None ou vazio
                try:
                    url = get_url_s3(imagem_key, expires_in=604800)
                    print(f"URL gerada: {url is not None}")
                    
                    if url:
                        session = requests.Session()
                        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
                        session.mount('https://', HTTPAdapter(max_retries=retries))
                        
                        print("Baixando imagem do S3...")
                        response = session.get(url, timeout=30)
                        response.raise_for_status()
                        print(f"Imagem baixada: {len(response.content)} bytes")
                        
                        pil_img = Image.open(BytesIO(response.content))
                        print(f"Imagem aberta: {pil_img.size}")
                        
                        # Redimensionar para caber no placeholder
                        pil_img = pil_img.resize((200, 200), Image.Resampling.LANCZOS)
                        
                        ctk_img = ctk.CTkImage(light_image=pil_img, size=(200, 200))
                        
                        # Limpar label anterior e adicionar imagem
                        self.img_label.destroy()
                        self.img_label = ctk.CTkLabel(
                            self.img_placeholder,
                            image=ctk_img,
                            text="",
                            fg_color="#F8FAFC"
                        )
                        self.img_label.image = ctk_img  # Manter referência
                        self.img_label.pack(fill="both", expand=True)
                        print("Imagem exibida com sucesso!")
                except Exception as e:
                    print(f"Erro ao carregar foto do S3: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Nenhuma imagem armazenada para este pet (chave: {imagem_key})")
        except Exception as e:
            print(f"Erro ao verificar imagem do pet: {e}")
            import traceback
            traceback.print_exc()

    def escolher_foto_pet(self):
        """Abre diálogo para escolher foto do pet"""
        file_path = filedialog.askopenfilename(
            title="Selecione uma foto para o pet",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos", "*.*")]
        )
        
        if file_path:
            self._fazer_upload_foto_pet(file_path)

    def _fazer_upload_foto_pet(self, file_path):
        """Faz upload da foto para o S3 e atualiza o banco"""
        try:
            # Fazer upload no S3
            imagem_key = upload_foto_pet_s3(file_path, self.pet_atual_id)
            
            if not imagem_key:
                messagebox.showerror("Erro", "Falha ao fazer upload da foto")
                return
            
            # Atualizar no banco de dados
            sucesso = self.pet_controller.atualizar_imagem_pet(self.pet_atual_id, imagem_key)
            
            if sucesso:
                # Carregar a nova foto
                try:
                    pil_img = Image.open(file_path)
                    pil_img = pil_img.resize((200, 200), Image.Resampling.LANCZOS)
                    
                    ctk_img = ctk.CTkImage(light_image=pil_img, size=(200, 200))
                    
                    # Atualizar label com nova imagem
                    self.img_label.destroy()
                    self.img_label = ctk.CTkLabel(
                        self.img_placeholder,
                        image=ctk_img,
                        text=""
                    )
                    self.img_label.image = ctk_img
                    self.img_label.pack(fill="both", expand=True)
                    
                    messagebox.showinfo("Sucesso", "Foto do pet atualizada com sucesso!")
                except Exception as e:
                    print(f"Erro ao exibir foto: {e}")
                    messagebox.showwarning("Aviso", "Foto salva no banco mas não foi possível exibir")
            else:
                messagebox.showerror("Erro", "Falha ao atualizar foto no banco de dados")
        except Exception as e:
            print(f"Erro ao fazer upload: {e}")
            messagebox.showerror("Erro", f"Erro ao processar foto: {str(e)}")

    def mudar_aba_pet(self, aba):
        self.active_aba = aba
        
        # Atualiza a cor dos botões para saber qual está ativa
        for chave, btn in self.abas_botoes.items():
            if chave == aba:
                btn.configure(fg_color="#14B8A6", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#1E293B")

        # Limpa o container para desenhar a nova aba
        for w in self.container_abas.winfo_children():
            w.destroy()

        # Chama a função de renderização correspondente
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
            text="Medicamentos em Uso",
            font=("Arial", 18, "bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ NOVO MEDICAMENTO",
            fg_color="#14B8A6",
            font=("Arial", 11, "bold"),
            height=35,
            corner_radius=8,
            command=self.abrir_modal_novo_medicamento
        ).pack(side="right")

        list_frame = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        list_frame.pack(fill="both", expand=True)

        # 🔥 AQUI ESTÁ O QUE FALTAVA
        medicamentos = self.pet_controller.buscar_medicamentos_por_pet(self.pet_atual_id)

        if not medicamentos:
            empty_card = ctk.CTkFrame(
                list_frame,
                fg_color="transparent",
                border_width=1,
                border_color="#F1F5F9",
                corner_radius=15,
                height=100
            )
            empty_card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                empty_card,
                text="Nenhum medicamento registrado.",
                font=("Arial", 12, "italic"),
                text_color="#94A3B8"
            ).place(relx=0.5, rely=0.5, anchor="center")

        else:
            for med in medicamentos:
                card = ctk.CTkFrame(
                    list_frame,
                    fg_color="white",
                    corner_radius=12,
                    border_width=1,
                    border_color="#F1F5F9"
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
                    font=("Arial", 12)
                ).pack(anchor="w", padx=15, pady=12)

    def _renderizar_aba_emocional(self):
        # 1. Busca os dados reais do banco através do controller
        historico = self.pet_controller.buscar_historico_emocional(self.pet_atual_id)
        
        # Se não houver dados, cria um estado vazio para não quebrar o gráfico
        if not historico:
            from datetime import datetime
            datas = [
                datetime.strptime(h.get('DATA'), "%Y-%m-%d").strftime("%d/%m")
                for h in historico
            ]
            niveis = [0]
            status_humor = "Não registrado"
            emoji_humor = "❓"
            nota_tutor = "Nenhuma nota registrada."
        else:
            # Prepara os dados para o Matplotlib
            datas = [h.get('data', '') for h in historico]
            niveis = [h.get('nivel', 0) for h in historico]
            
            # Pega o registro mais recente para os cards laterais
            ultimo = historico[-1]
            nota_tutor = ultimo.get('nota', 'Sem observações')
            nivel_atual = ultimo.get('nivel', 0)
            
            # Lógica de humor baseada no nível (exemplo: 1-Triste, 2-Estável, 3-Feliz)
            mapping = {3: ("Muito Feliz", "😊"), 2: ("Estável", "😐"), 1: ("Amuado", "😔")}
            status_humor, emoji_humor = mapping.get(nivel_atual, ("Indefinido", "😶"))

        # --- LAYOUT DO GRÁFICO ---
        main_row = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        main_row.pack(fill="both", expand=True)

        chart_container = ctk.CTkFrame(main_row, fg_color="white", corner_radius=20, border_width=1, border_color="#F1F5F9")
        chart_container.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(chart_container, text="Bem-estar do Pet", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(chart_container, text="TENDÊNCIA SEMANAL", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=20)

        # Matplotlib usando as listas 'datas' e 'niveis' vindas do banco
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('white')
        
        ax.plot(datas, niveis, color="#14B8A6", marker='o', linewidth=3, markersize=8)
        ax.fill_between(datas, niveis, color="#14B8A6", alpha=0.1)
        
        ax.set_ylim(0, 4) # Escala de 0 a 3 (ou 4 para dar margem)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["😔", "😐", "😊"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # --- CARDS LATERAIS ---
        right_panel = ctk.CTkFrame(main_row, fg_color="transparent", width=250)
        right_panel.pack(side="left", fill="y")

        humor_card = ctk.CTkFrame(right_panel, fg_color="#14B8A6", corner_radius=20)
        humor_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(humor_card, text="HUMOR REGISTRADO", font=("Arial", 9, "bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(humor_card, text=emoji_humor, font=("Arial", 40)).pack()
        ctk.CTkLabel(humor_card, text=status_humor, font=("Arial", 16, "bold"), text_color="white").pack(pady=(5, 15))

        nota_card = ctk.CTkFrame(right_panel, fg_color="#F8FAFC", corner_radius=15)
        nota_card.pack(fill="x")
        ctk.CTkLabel(nota_card, text="💬 NOTA DO TUTOR", font=("Arial", 9, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(nota_card, text=f'"{nota_tutor}"', font=("Arial", 12, "italic"), text_color="#64748B", wraplength=200).pack(anchor="w", padx=15, pady=(5, 15))
        
    def abrir_modal_novo_medicamento(self):
        self.overlay_med = ctk.CTkFrame(self.content.master, fg_color="#000000")
        self.overlay_med.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay_med,
            width=500,
            height=600,
            corner_radius=30,
            fg_color="#F8FAFC"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(
            modal,
            text="Novo Medicamento",
            font=("Arial", 24, "bold"),
            text_color="#1E293B"
        ).pack(pady=(30, 20))

        def criar_input(placeholder):
            entry = ctk.CTkEntry(
                modal,
                placeholder_text=placeholder,
                height=50,
                corner_radius=20,
                border_width=0,
                fg_color="#E2E8F0",
                text_color="#1E293B"
            )
            entry.pack(fill="x", padx=50, pady=10)
            return entry

        self.ent_med_nome = criar_input("Nome do Medicamento")
        self.ent_med_dose = criar_input("Dosagem (ex: 50mg)")
        self.ent_med_freq = criar_input("Frequência (ex: 2x ao dia)")

        self.ent_med_inicio = criar_input("Data de Início (dd/mm/aaaa)")
        self.ent_med_fim = criar_input("Data de Término (dd/mm/aaaa)")

        btn_box = ctk.CTkFrame(modal, fg_color="transparent")
        btn_box.pack(fill="x", padx=50, pady=30)

        ctk.CTkButton(
            btn_box,
            text="Cancelar",
            fg_color="#E2E8F0",
            text_color="#1E293B",
            height=50,
            corner_radius=20,
            command=lambda: self.overlay_med.destroy()
        ).pack(side="left", expand=True, padx=10)

        ctk.CTkButton(
            btn_box,
            text="Adicionar à Lista",
            fg_color="#14B8A6",
            hover_color="#0D9488",
            height=50,
            corner_radius=20,
            font=("Arial", 13, "bold"),
            command=self.salvar_novo_medicamento
        ).pack(side="right", expand=True, padx=10)


    

    def salvar_novo_medicamento(self):
        nome = self.ent_med_nome.get().strip()
        dose = self.ent_med_dose.get().strip()
        freq = self.ent_med_freq.get().strip()
        inicio = self.ent_med_inicio.get().strip()   # ← AGORA EXISTE
        fim = self.ent_med_fim.get().strip()         # ← AGORA EXISTE

        if not nome:
            messagebox.showwarning("Aviso", "Digite o nome do medicamento")
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
            messagebox.showerror("Erro", "Use o formato DD/MM/AAAA para as datas")
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
            messagebox.showinfo("Sucesso", "Medicamento adicionado!")
            self.overlay_med.destroy()
            self.mudar_aba_pet("medicamentos")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar.")

    def abrir_modal_nova_vacina(self):
        """Abre modal para adicionar nova vacina"""
        self.overlay_vacina = ctk.CTkFrame(self.content.master, fg_color="#1A1A1A")
        self.overlay_vacina.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Modal
        self.modal_vacina = ctk.CTkFrame(
        self.overlay_vacina, 
        width=420,
        corner_radius=20, 
        border_width=2, 
        border_color="#14B8A6", 
        fg_color="white"
        )
        self.modal_vacina.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone de seringa
        ctk.CTkLabel(
            self.modal_vacina, 
            text="💉", 
            font=("Arial", 40)
        ).pack(pady=(20, 10))

        # Título
        ctk.CTkLabel(
            self.modal_vacina, 
            text="Novo Registro", 
            font=("Arial", 22, "bold"), 
            text_color="#14B8A6"
        ).pack(pady=(0, 5))

        # Subtítulo
        ctk.CTkLabel(
            self.modal_vacina, 
            text="Insira os dados da aplicação abaixo.", 
            font=("Arial", 12), 
            text_color="#94A3B8"
        ).pack(pady=(0, 20))

        # Form
        form = ctk.CTkFrame(self.modal_vacina, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # Campo nome da vacina
        ctk.CTkLabel(form, text="Nome da Vacina", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
        self.entry_nome_vacina = ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1")
        self.entry_nome_vacina.pack(fill="x", pady=(2, 15))

        # Campo data de aplicação
        ctk.CTkLabel(form, text="Data de Aplicação", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 0))
        self.entry_data_aplicacao = ctk.CTkEntry(
            form, 
            placeholder_text="dd/mm/aaaa", 
            height=40, 
            corner_radius=10, 
            border_color="#CBD5E1"
        )
        self.entry_data_aplicacao.pack(fill="x", pady=(2, 15))

        # Campo próxima dose
        ctk.CTkLabel(form, text="Próxima Dose", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 0))
        self.entry_proxima_dose = ctk.CTkEntry(
            form, 
            placeholder_text="dd/mm/aaaa", 
            height=40, 
            corner_radius=10, 
            border_color="#CBD5E1"
        )
        self.entry_proxima_dose.pack(fill="x", pady=(2, 20))

        # Botões
        btn_container = ctk.CTkFrame(self.modal_vacina, fg_color="transparent")
        btn_container.pack(fill="x", pady=20, padx=30)

        btn_container.columnconfigure((0, 1), weight=1)

        btn_cancelar = ctk.CTkButton(
            btn_container, 
            text="CANCELAR", 
            fg_color="#E2E8F0", 
            text_color="#1E293B",
            font=("Arial", 13, "bold"),
            height=50,
            corner_radius=10,
            command=self.fechar_modal_vacina
        )
        btn_cancelar.grid(row=0, column=0, padx=6, sticky="ew")

        btn_salvar = ctk.CTkButton(
            btn_container, 
            text="SALVAR REGISTRO", 
            fg_color="#14B8A6", 
            text_color="white",
            font=("Arial", 13, "bold"),
            height=50,
            corner_radius=10,
            command=self.salvar_nova_vacina
        )
        btn_salvar.grid(row=0, column=1, padx=6, sticky="ew")


    def fechar_modal_vacina(self):
        """Fecha o modal de nova vacina"""
        if hasattr(self, 'overlay_vacina') and self.overlay_vacina:
            self.overlay_vacina.destroy()

    def salvar_nova_vacina(self):
        """Salva a nova vacina no banco de dados"""
        from datetime import datetime
        
        nome_vacina = self.entry_nome_vacina.get().strip()
        proxima_dose = self.entry_proxima_dose.get().strip()

        if not nome_vacina:
            messagebox.showwarning("Aviso", "Por favor, insira o nome da vacina")
            return

        if not proxima_dose:
            messagebox.showwarning("Aviso", "Por favor, insira a data da próxima dose")
            return

        # Converte a data de DD/MM/YYYY para YYYY-MM-DD
        try:
            data_obj = datetime.strptime(proxima_dose, "%d/%m/%Y")
            proxima_dose_formatada = data_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/YYYY")
            return

        # Tenta adicionar ao banco
        sucesso = self.pet_controller.adicionar_vacina(
            self.pet_atual_id, 
            nome_vacina, 
            proxima_dose_formatada
        )

        if sucesso:
            messagebox.showinfo("Sucesso", "Vacina registrada com sucesso!")
            self.fechar_modal_vacina()
            # Atualiza a lista de vacinas
            self.mudar_aba_pet("saude")
        else:
            messagebox.showerror("Erro", "Falha ao registrar a vacina")

    def _carregar_foto_card(self, label, imagem_key):
        """Carrega foto do S3 para exibir no card de pacientes"""
        try:
            if not imagem_key or not str(imagem_key).strip():
                return
            
            url = get_url_s3(imagem_key, expires_in=604800)
            
            if url:
                session = requests.Session()
                retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
                session.mount('https://', HTTPAdapter(max_retries=retries))
                
                response = session.get(url, timeout=30)
                response.raise_for_status()
                
                pil_img = Image.open(BytesIO(response.content))
                # Redimensionar para caber no card
                pil_img = pil_img.resize((130, 130), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(130, 130))
                
                # Atualizar label com a foto
                label.configure(image=ctk_img, text="")
                label.image = ctk_img  # Manter referência
        except Exception as e:
            print(f"Erro ao carregar foto no card: {e}")
