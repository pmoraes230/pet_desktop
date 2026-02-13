from msvcrt import locking
import customtkinter as ctk
import boto3
import os
from tkinter import filedialog
from io import BytesIO

from app.core import app
from app.utils.loading_overlay import run_with_loading
from ..services.s3_client import get_url_s3, upload_foto_s3
from ..config.database import connectdb
from app.models.mudar_foto import salvar_nova_foto
from tkinter import filedialog
import requests

from PIL import Image, ImageDraw

def criar_imagem_redonda(pil_img, size):
    pil_img = pil_img.resize(size).convert("RGBA")

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)

    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(pil_img, (0, 0), mask)

    return output

class ModuloConfiguracoes:
    def __init__(self, content_frame=None, parent=None):
        # content_frame: frame onde as telas serão renderizadas (ex.: Dashboard.content)
        # parent: referência ao dashboard (opcional) para acessar métodos como atualizar_avatar_topo
        self.content = content_frame
        self.parent = parent
        self.current_user_id = None
        self.foto_perfil = None

    # --- TELA: EDITAR PERFIL ---
    def tela_configuracoes_perfil(self):
        if not self.content:
            print("Erro: content onde renderizar não fornecido.")
            return

        # tenta obter dados do dashboard pai quando disponível
        self.current_user_id = getattr(self.parent, 'current_user_id', None)
        self.foto_perfil = getattr(self.parent, 'foto_perfil', None)

        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(scroll, text="Editar Perfil Profissional", font=("Arial", 24, "bold"), text_color="#1E293B").pack(pady=(0, 30))
        
        # Card da Foto
        foto_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=50, border_width=1, border_color="#E2E8F0")
        foto_card.pack(fill="x", pady=(0, 20))
        
        foto_cont = ctk.CTkFrame(foto_card, fg_color="transparent")
        foto_cont.pack(pady=30)
        
        av = ctk.CTkFrame(foto_cont, width=120, height=120, corner_radius=60,
                  fg_color="#F1F5F9", border_width=4, border_color="#14B8A6")
        av.pack()
        av.pack_propagate(False)

        self.avatar_label = ctk.CTkLabel(av, text="U", font=("Arial", 40, "bold"), text_color="#14B8A6")
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            foto_cont,
            text="📷",
            width=35,
            height=35,
            corner_radius=19,
            fg_color="#14B8A6",
            command=self.escolher_nova_foto 
        ).place(relx=0.9, rely=0.9, anchor="center")

        # Carregar foto já existente do usuário
        try:
            perfil = self.foto_perfil.fetch_perfil_data() if self.foto_perfil else {}
            key = perfil.get("imagem_perfil_veterinario")

            if key:
                url = get_url_s3(key, expires_in=86400)
                if not url:
                    raise Exception("Falha ao gerar URL assinada")

                response = requests.get(url, timeout=10)
                response.raise_for_status()

                img = Image.open(BytesIO(response.content))
                img = criar_imagem_redonda(img, (110, 110))

                self.preview_img = ctk.CTkImage(light_image=img, size=(110, 110))
                self.avatar_label.configure(image=self.preview_img, text="")
                self.avatar_label.image = self.preview_img

        except Exception as e:
            print("Erro ao carregar foto existente:", e)
        
        # Card dos Dados
        dados = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        dados.pack(fill="x", pady=(0, 30))
        ctk.CTkLabel(dados, text="👤  Dados Pessoais", font=("Arial", 16, "bold")).pack(anchor="w", padx=30, pady=20)
        
        grid = ctk.CTkFrame(dados, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=(0, 20)); grid.columnconfigure((0, 1), weight=1)
        
        # Campos editáveis — manter referências para leitura/salvamento
        self.entry_nome = self.criar_campo_input(grid, "NOME COMPLETO", "", 0, 0)
        self.entry_email = self.criar_campo_input(grid, "E-MAIL", "", 0, 1)
        self.entry_crmv = self.criar_campo_input(grid, "CRMV", "", 1, 0)
        self.entry_uf = self.criar_campo_input(grid, "ESTADO (UF)", "", 1, 1)

        # Preencher com dados do banco quando disponível
        try:
            perfil = self.foto_perfil.fetch_perfil_data() if self.foto_perfil else {}
            if perfil:
                self.entry_nome.delete(0, 'end'); self.entry_nome.insert(0, perfil.get('NOME', ''))
                self.entry_email.delete(0, 'end'); self.entry_email.insert(0, perfil.get('EMAIL', ''))
                self.entry_crmv.delete(0, 'end'); self.entry_crmv.insert(0, perfil.get('CRMV', ''))
                self.entry_uf.delete(0, 'end'); self.entry_uf.insert(0, perfil.get('UF_CRMV', ''))
        except Exception as e:
            print('Erro ao preencher campos do perfil:', e)

        # Botão salvar
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Salvar", fg_color="#14B8A6", command=self.salvar_perfil).pack(anchor="e", padx=30, pady=10)

    def escolher_nova_foto(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        # Função que faz o trabalho (será executada em thread separada)
        def tarefa():
            key = salvar_nova_foto(self.current_user_id, file_path)
            
            if not key:
                print("Falha ao salvar foto no S3")
                return None  # ou raise Exception se preferir

            self.atualizar_preview_foto(file_path)
            
            if self.parent and hasattr(self.parent, "atualizar_avatar_topo"):
                self.parent.atualizar_avatar_topo(key)
                print("Foto atualizada com sucesso!")
            else:
                print("Aviso: parent não tem método atualizar_avatar_topo")
            
            return key

        # Isso já cuida de mostrar/esconder o loading automaticamente
        run_with_loading(
            tarefa,
            message="Enviando foto... Aguarde"
        )

    def atualizar_preview_foto(self, file_path):
        img = Image.open(file_path)
        img = criar_imagem_redonda(img, (120, 120))

        self.preview_img = ctk.CTkImage(light_image=img, size=(120, 120))


        self.avatar_label.configure(image=self.preview_img, text="")
        self.avatar_label.image = self.preview_img  # 👈 impede sumir

    # --- TELA: CONFIGURAÇÕES GERAIS ---
    def tela_configuracoes_gerais(self):
        if not self.content:
            print("Erro: content onde renderizar não existe")
            return

        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(scroll, text="Configurações da Conta", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Idioma
        c_lang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_lang.pack(fill="x", pady=10)
        ctk.CTkLabel(c_lang, text="🌐 Idioma", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=20)
        ctk.CTkOptionMenu(c_lang, values=["Português", "English"], fg_color="#F8FAFC", text_color="black").pack(side="right", padx=20)
        
        
        # Notificações
        c_not = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_not.pack(fill="x", pady=10)
        ctk.CTkLabel(c_not, text="🔔 Notificações", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=15)
        
        for t in ["E-mail", "Lembretes", "Dicas semanais"]:
            f = ctk.CTkFrame(c_not, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=t).pack(side="left")
            ctk.CTkSwitch(f, text="").pack(side="right")

        # --- SEÇÃO: ALTERAR SENHA (ADICIONADA) ---
        c_senha = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_senha.pack(fill="x", pady=10)
        ctk.CTkLabel(c_senha, text="🔒 Segurança da conta", font=("Arial", 14, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(c_senha, text="Atualize sua senha periodicamente para manter seu perfil seguro.", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkButton(c_senha, text="Mudar senha", fg_color="#14B8A6", text_color="white", font=("Arial", 13, "bold"), 
                  command=lambda: (self.parent.trocar_tela(self.tela_configuracoes_senha) if self.parent and hasattr(self.parent, 'trocar_tela') else self.tela_configuracoes_senha())).pack(anchor="w", padx=20, pady=15)
    
            
        # Perigo (Desativar)
        c_dang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#FCA5A5")
        c_dang.pack(fill="x", pady=20)
        ctk.CTkLabel(c_dang, text="⚠️ Desativar conta", font=("Arial", 14, "bold"), text_color="#EF4444").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(c_dang, text="Essa ação não pode ser desfeita.", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkButton(c_dang, text="Desativar", fg_color="#EF4444", command=self.mostrar_modal).pack(anchor="w", padx=20, pady=15)

    # --- AUXILIARES ---
    def mostrar_modal(self):
        parent_widget = self.content.master if self.content else None
        if not parent_widget:
            print("Erro: não há widget pai para mostrar modal")
            return

        self.m_bg = ctk.CTkFrame(parent_widget, fg_color="black")
        self.m_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.m_box = ctk.CTkFrame(parent_widget, width=300, height=200, corner_radius=20)
        self.m_box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.m_box, text="Tem certeza?", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkButton(self.m_box, text="Cancelar", command=lambda:[self.m_bg.destroy(), self.m_box.destroy()]).pack(pady=5)

    def criar_campo_input(self, master, label_text, placeholder, row, col):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        ctk.CTkLabel(f, text=label_text, font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=5)
        e = ctk.CTkEntry(f, height=45, corner_radius=12, border_width=0, fg_color="#F8FAFC", text_color="#1E293B", font=("Arial", 13, "bold"))
        if placeholder:
            e.insert(0, placeholder)
        e.pack(fill="x", pady=5)
        return e


    def salvar_perfil(self):
        """Coleta os valores dos campos e atualiza o banco de dados."""
        if not self.current_user_id:
            print("Erro: usuário atual não definido")
            return

        data = {
            'NOME': self.entry_nome.get().strip(),
            'EMAIL': self.entry_email.get().strip(),
            'CRMV': self.entry_crmv.get().strip(),
            'UF_CRMV': self.entry_uf.get().strip()
        }

        def tarefa():
            # usa o controller já disponível em self.foto_perfil
            if not self.foto_perfil:
                print('Erro: controlador de perfil não disponível')
                return False

            success = False
            try:
                success = self.foto_perfil.update_perfil(data)
            except Exception as e:
                print('Erro ao atualizar perfil:', e)
                success = False

            if success:
                print('Perfil salvo com sucesso')
            else:
                print('Falha ao salvar perfil')

            return success

        run_with_loading(tarefa, message='Salvando perfil... Aguarde')


    def tela_configuracoes_senha(self):
        """Tela simples para alterar senha (placeholder)."""
        if not self.content:
            print("Erro: content não definido para tela de senha")
            return

        for w in self.content.winfo_children():
            w.destroy()

        frm = ctk.CTkFrame(self.content, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=40, pady=40)
        ctk.CTkLabel(frm, text="Mudar Senha", font=("Arial", 22, "bold")).pack(pady=10)
        ctk.CTkEntry(frm, placeholder_text="Senha atual", show="*").pack(fill="x", pady=5)
        ctk.CTkEntry(frm, placeholder_text="Nova senha", show="*").pack(fill="x", pady=5)
        ctk.CTkEntry(frm, placeholder_text="Confirmar nova senha", show="*").pack(fill="x", pady=5)
        ctk.CTkButton(frm, text="Salvar", fg_color="#14B8A6").pack(pady=10)


    