import customtkinter as ctk
import boto3
import os
from tkinter import filedialog
from io import BytesIO
from ..services.s3_client import upload_foto_s3
from ..config.database import connectdb
from app.models.mudar_foto import salvar_nova_foto
from tkinter import filedialog

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
    def __init__(self, content_frame):
        self.content = content_frame

    # --- TELA: EDITAR PERFIL ---
    def tela_configuracoes_perfil(self):
        self.current_user_id
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(scroll, text="Editar Perfil Profissional", font=("Arial", 24, "bold"), text_color="#1E293B").pack(pady=(0, 30))
        
        foto_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
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
            corner_radius=17,
            fg_color="#14B8A6",
            command=self.escolher_nova_foto  # 👈 agora funciona
        ).place(relx=0.9, rely=0.9, anchor="center")

        # Carregar foto já existente do usuário
        try:
            perfil = self.foto_perfil.fetch_perfil_data()
            key = perfil.get("imagem_perfil_veterinario")

            if key:
                url = f"https://coracao-em-patas.s3.amazonaws.com/{key}"
                s3 = boto3.client("s3")
                bucket = "coracao-em-patas"

                obj = s3.get_object(Bucket=bucket, Key=key)
                img = Image.open(BytesIO(obj["Body"].read()))
                img = criar_imagem_redonda(img, (110, 110))  # EXTRA AQUI

                self.preview_img = ctk.CTkImage(light_image=img, size=(110, 110))  # EXTRA AQUI



                self.avatar_label.configure(image=self.preview_img, text="")
                self.avatar_label.image = self.preview_img

        except Exception as e:
            print("Erro ao carregar foto existente:", e)


        
        dados = ctk.CTkFrame(scroll, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        dados.pack(fill="x", pady=(0, 30))
        ctk.CTkLabel(dados, text="👤  Dados Pessoais", font=("Arial", 16, "bold")).pack(anchor="w", padx=30, pady=20)
        
        grid = ctk.CTkFrame(dados, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=(0, 20))
        grid.columnconfigure((0, 1), weight=1)
        
        self.criar_campo_input(grid, "NOME COMPLETO", "Usuário Exemplo", 0, 0)
        self.criar_campo_input(grid, "E-MAIL", "usuario@email.com", 0, 1)
        self.criar_campo_input(grid, "CRMV", "12345-SP", 1, 0)
        self.criar_campo_input(grid, "ESTADO (UF)", "São Paulo", 1, 1)
    def escolher_nova_foto(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        # 1. Salva no S3 e no Banco (isso você já faz)
        key = salvar_nova_foto(self.current_user_id, file_path)

        if key:
            # 2. Atualiza o preview grande da tela de edição (onde você está)
            self.atualizar_preview_foto(file_path)
            
            # 3. CORREÇÃO AQUI: Chama o método do dashboard diretamente
            # Não use self.master, use apenas self
            if hasattr(self, "atualizar_avatar_topo"):
                self.atualizar_avatar_topo(key)

            print("Foto atualizada com sucesso!")
        else:
            print("Falha ao atualizar foto.")

    def atualizar_preview_foto(self, file_path):
        img = Image.open(file_path)
        img = criar_imagem_redonda(img, (120, 120))

        self.preview_img = ctk.CTkImage(light_image=img, size=(120, 120))


        self.avatar_label.configure(image=self.preview_img, text="")
        self.avatar_label.image = self.preview_img  # 👈 impede sumir

        
        


    # --- TELA: CONFIGURAÇÕES GERAIS ---
    def tela_configuracoes_gerais(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(scroll, text="Configurações da Conta", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        c_lang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_lang.pack(fill="x", pady=10)
        ctk.CTkLabel(c_lang, text="🌐 Idioma", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=20)
        ctk.CTkOptionMenu(c_lang, values=["Português", "English"], fg_color="#F8FAFC", text_color="black").pack(side="right", padx=20)
        
        c_not = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_not.pack(fill="x", pady=10)
        ctk.CTkLabel(c_not, text="🔔 Notificações", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=15)
        
        for t in ["E-mail", "Lembretes", "Dicas semanais"]:
            f = ctk.CTkFrame(c_not, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=t).pack(side="left")
            ctk.CTkSwitch(f, text="").pack(side="right")

        c_senha = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        c_senha.pack(fill="x", pady=10)
        ctk.CTkLabel(c_senha, text="🔒 Segurança da conta", font=("Arial", 14, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(c_senha, text="Atualize sua senha periodicamente para manter seu perfil seguro.", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkButton(c_senha, text="Mudar senha", fg_color="#14B8A6", text_color="white", font=("Arial", 13, "bold"),
                      command=lambda: print("Trocar para tela de senha (implementar)")).pack(anchor="w", padx=20, pady=15)
        
        c_dang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#FCA5A5")
        c_dang.pack(fill="x", pady=20)
        ctk.CTkLabel(c_dang, text="⚠️ Desativar conta", font=("Arial", 14, "bold"), text_color="#EF4444").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(c_dang, text="Essa ação não pode ser desfeita.", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkButton(c_dang, text="Desativar", fg_color="#EF4444", command=self.mostrar_modal).pack(anchor="w", padx=20, pady=15)

    def mostrar_modal(self):
        root = self.content.winfo_toplevel()  # pega a janela principal
        self.m_bg = ctk.CTkFrame(root, fg_color="black")
        self.m_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.m_box = ctk.CTkFrame(root, width=300, height=200, corner_radius=20)
        self.m_box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.m_box, text="Tem certeza?", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkButton(self.m_box, text="Cancelar", command=lambda: [self.m_bg.destroy(), self.m_box.destroy()]).pack(pady=5)

    def criar_campo_input(self, master, label_text, placeholder, row, col):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        ctk.CTkLabel(f, text=label_text, font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=5)
        e = ctk.CTkEntry(f, height=45, corner_radius=12, border_width=0, fg_color="#F8FAFC", text_color="#1E293B", font=("Arial", 13, "bold"))
        e.insert(0, placeholder)
        e.pack(fill="x", pady=5)


    