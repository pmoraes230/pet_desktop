from doctest import master
import customtkinter as ctk
from ..models.pets_vet import PetAll
from ..controllers.pet_controller import PetController

class ModuloPacientes:

    def __init__(self, content, trocar_tela):
        self.content = content
        self.trocar_tela = trocar_tela
        self.pet_controller = PetController()

    def tela_pacientes(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))   
        ctk.CTkLabel(header, text="Pacientes", font=("Arial", 28, "bold")).pack(side="left")  
        ctk.CTkButton(header, text="+ Novo Paciente", fg_color="#14B8A6", hover_color="#0D9488", width=150, corner_radius=10, command=self.abrir_popup_novo_paciente).pack(side="right")
        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 30))
        ctk.CTkEntry(search_row, placeholder_text="🔍 Pesquise por tutor ou pet", height=45, corner_radius=22).pack(side="left", fill="x", expand=True, padx=(0, 15))      
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)  

        pets = PetAll.listar_pets()

        for i, pet in enumerate(pets):
            emoji = "🐶" if pet["especie"] == "Cachorro" else "🐱"
            info = f'{pet["raca"]} • {pet["idade"]} Anos'

            self.criar_card_paciente(
                grid,
                pet["nome_pet"],
                "Saudável",
                info,
                emoji,
                i % 3
            )

        pets = self.pet_controller.listar_pets()

        for i, pet in enumerate(pets):
            emoji = "🐶" if pet["especie"] == "Cachorro" else "🐱"
            info = f'{pet["raca"]} • {pet["idade"]} Anos'

            row = i // 3
            col = i % 3

            self.criar_card_paciente(
                grid,
                pet["nome_pet"],
                "Saudável",
                info,
                emoji,
                row,
                col
            )




    def abrir_popup_novo_paciente(self):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.modal_frame = ctk.CTkFrame(self.overlay, width=400, height=520, corner_radius=20, border_width=2, border_color="#14B8A6")
        self.modal_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.modal_frame.pack_propagate(False)
        ctk.CTkLabel(self.modal_frame, text="🐾 Novo Paciente", font=("Arial", 22, "bold"), text_color="#14B8A6").pack(pady=20)
        form = ctk.CTkFrame(self.modal_frame, fg_color="transparent"); form.pack(fill="both", expand=True, padx=30)

        def criar_input(label):
            ctk.CTkLabel(form, text=label, font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1")
            entry.pack(fill="x", pady=(2, 5))
            return entry

        criar_input("Nome do Pet"); criar_input("Nome do Tutor"); criar_input("Telefone de Contato")
        ctk.CTkLabel(form, text="Observações Iniciais", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form, height=40, corner_radius=10, border_color="#CBD5E1").pack(fill="x", pady=(2, 5))

        btn_container = ctk.CTkFrame(self.modal_frame, fg_color="transparent"); btn_container.pack(fill="x", pady=25, padx=30)
        ctk.CTkButton(btn_container, text="Confirmar", fg_color="#14B8A6", width=160, height=40, command=self.fechar_popup).pack(side="left", padx=5)
        ctk.CTkButton(btn_container, text="Cancelar", fg_color="#94A3B8", width=160, height=40, command=self.fechar_popup).pack(side="right", padx=5)

    def fechar_popup(self):
        self.overlay.destroy()

    def tela_perfil_pet(self, nome_pet, raca_pet, emoji):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=30)
        container = ctk.CTkFrame(scroll, fg_color="transparent"); container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0); container.columnconfigure(1, weight=1)

        card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, width=350, border_width=1, border_color="#F1F5F9")
        card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        img_placeholder = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", height=220, corner_radius=30); img_placeholder.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(img_placeholder, text=emoji, font=("Arial", 80)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card_esq, text=nome_pet, font=("Arial", 32, "bold"), text_color="#1E293B").pack()
        ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Arial", 12, "bold"), text_color="#14B8A6").pack(pady=(0, 20))
        
        tutor_box = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", corner_radius=15); tutor_box.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(tutor_box, text="TUTOR RESPONSÁVEL", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(tutor_box, text="Ana Souza", font=("Arial", 14, "bold"), text_color="#1E293B").pack(anchor="w", padx=15, pady=(0, 10))

        row_stats = ctk.CTkFrame(card_esq, fg_color="transparent"); row_stats.pack(fill="x", padx=20, pady=20)
        p_box = ctk.CTkFrame(row_stats, fg_color="#F0FDFA", corner_radius=15, height=80); p_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(p_box, text="PESO", font=("Arial", 10, "bold"), text_color="#134E4A").pack(pady=(10, 0))
        ctk.CTkLabel(p_box, text="12 kg", font=("Arial", 18, "bold"), text_color="#134E4A").pack()
        s_box = ctk.CTkFrame(row_stats, fg_color="#EFF6FF", corner_radius=15, height=80); s_box.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(s_box, text="SEXO", font=("Arial", 10, "bold"), text_color="#1E3A8A").pack(pady=(10, 0))
        ctk.CTkLabel(s_box, text="Macho", font=("Arial", 18, "bold"), text_color="#1E3A8A").pack()

        prox_c = ctk.CTkFrame(card_esq, fg_color="#14B8A6", corner_radius=30); prox_c.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(prox_c, text="15 de Fev", font=("Arial", 28, "bold"), text_color="white").pack(anchor="w", padx=20)

        self.right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=40, border_width=1, border_color="#F1F5F9"); self.right_col.grid(row=0, column=1, sticky="nsew")
        tab_header = ctk.CTkFrame(self.right_col, fg_color="#F1F5F9", corner_radius=25, height=50); tab_header.pack(pady=30, padx=30, anchor="w")
        self.btn_sobre = ctk.CTkButton(tab_header, text="SOBRE", width=120, corner_radius=25, fg_color="#14B8A6", text_color="white", command=lambda: self.mudar_aba_pet("sobre")); self.btn_sobre.pack(side="left", padx=2, pady=2)
        self.btn_saude = ctk.CTkButton(tab_header, text="SAÚDE", width=120, corner_radius=25, fg_color="transparent", text_color="#64748B", command=lambda: self.mudar_aba_pet("saude")); self.btn_saude.pack(side="left", padx=2, pady=2)

        self.container_abas = ctk.CTkFrame(self.right_col, fg_color="transparent"); self.container_abas.pack(fill="both", expand=True, padx=40)
        self.mudar_aba_pet("sobre")

    def mudar_aba_pet(self, aba):
        for w in self.container_abas.winfo_children(): w.destroy()
        if aba == "sobre":
            self.btn_sobre.configure(fg_color="#14B8A6", text_color="white")
            self.btn_saude.configure(fg_color="transparent", text_color="#64748B")
            ctk.CTkLabel(self.container_abas, text="📝 Observações Gerais", font=("Arial", 16, "bold")).pack(anchor="w")
            txt = ctk.CTkTextbox(self.container_abas, fg_color="#F8FAFC", corner_radius=20, height=150, border_width=1, border_color="#E2E8F0")
            txt.pack(fill="x", pady=15); txt.insert("1.0", "Pet dócil, porém agitado...")
        else:
            self.btn_saude.configure(fg_color="#14B8A6", text_color="white")
            self.btn_sobre.configure(fg_color="transparent", text_color="#64748B")
            vacinas = [("V10", "10/01/2026", "10/01/2027"), ("Raiva", "15/12/2025", "15/12/2026")]
            for n, d, p in vacinas:
                v_card = ctk.CTkFrame(self.container_abas, fg_color="white", corner_radius=25, border_width=1, border_color="#F1F5F9"); v_card.pack(fill="x", pady=10)
                ctk.CTkLabel(v_card, text=f"{n}\nAplicada: {d}", font=("Arial", 13, "bold"), justify="left").pack(side="left", padx=20)

    def criar_card_paciente(self, master, nome, status, info, icon, row, col):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=20, border_width=1)
        c.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
