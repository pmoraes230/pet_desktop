# screens/perfil_pet_screen.py
import customtkinter as ctk


def create_perfil_pet_screen(master, nome_pet, raca_pet, emoji):
    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=30)
    
    container = ctk.CTkFrame(scroll, fg_color="transparent")
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=0)
    container.columnconfigure(1, weight=1)

    # Card esquerdo - Perfil
    card_esq = ctk.CTkFrame(container, fg_color="white", corner_radius=40, width=350, border_width=1, border_color="#F1F5F9")
    card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
    
    img_placeholder = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", height=220, corner_radius=30)
    img_placeholder.pack(fill="x", padx=20, pady=20)
    ctk.CTkLabel(img_placeholder, text=emoji, font=("Arial", 80)).place(relx=0.5, rely=0.5, anchor="center")
    
    ctk.CTkLabel(card_esq, text=nome_pet, font=("Arial", 32, "bold"), text_color="#1E293B").pack()
    ctk.CTkLabel(card_esq, text=raca_pet.upper(), font=("Arial", 12, "bold"), text_color="#14B8A6").pack(pady=(0, 20))
    
    tutor_box = ctk.CTkFrame(card_esq, fg_color="#F8FAFC", corner_radius=15)
    tutor_box.pack(fill="x", padx=20, pady=10)
    ctk.CTkLabel(tutor_box, text="TUTOR RESPONSÁVEL", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
    ctk.CTkLabel(tutor_box, text="Ana Souza", font=("Arial", 14, "bold"), text_color="#1E293B").pack(anchor="w", padx=15, pady=(0, 10))

    row_stats = ctk.CTkFrame(card_esq, fg_color="transparent")
    row_stats.pack(fill="x", padx=20, pady=20)
    
    p_box = ctk.CTkFrame(row_stats, fg_color="#F0FDFA", corner_radius=15, height=80)
    p_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
    ctk.CTkLabel(p_box, text="PESO", font=("Arial", 10, "bold"), text_color="#134E4A").pack(pady=(10, 0))
    ctk.CTkLabel(p_box, text="12 kg", font=("Arial", 18, "bold"), text_color="#134E4A").pack()
    
    s_box = ctk.CTkFrame(row_stats, fg_color="#EFF6FF", corner_radius=15, height=80)
    s_box.pack(side="left", fill="both", expand=True, padx=(5, 0))
    ctk.CTkLabel(s_box, text="SEXO", font=("Arial", 10, "bold"), text_color="#1E3A8A").pack(pady=(10, 0))
    ctk.CTkLabel(s_box, text="Macho", font=("Arial", 18, "bold"), text_color="#1E3A8A").pack()

    prox_c = ctk.CTkFrame(card_esq, fg_color="#14B8A6", corner_radius=30)
    prox_c.pack(fill="x", padx=20, pady=20)
    ctk.CTkLabel(prox_c, text="Próxima consulta", font=("Arial", 14), text_color="white").pack(anchor="w", padx=20, pady=(15, 0))
    ctk.CTkLabel(prox_c, text="15 de Fev", font=("Arial", 28, "bold"), text_color="white").pack(anchor="w", padx=20)
    ctk.CTkLabel(prox_c, text="Vacinação", font=("Arial", 14), text_color="white").pack(anchor="w", padx=20, pady=(0, 15))

    # Coluna direita - Abas
    right_col = ctk.CTkFrame(container, fg_color="white", corner_radius=40, border_width=1, border_color="#F1F5F9")
    right_col.grid(row=0, column=1, sticky="nsew")
    
    tab_header = ctk.CTkFrame(right_col, fg_color="#F1F5F9", corner_radius=25, height=50)
    tab_header.pack(pady=30, padx=30, anchor="w")
    
    btn_sobre = ctk.CTkButton(
        tab_header, text="SOBRE", width=120, corner_radius=25,
        fg_color="#14B8A6", text_color="white",
        command=lambda: mudar_aba("sobre", right_col, btn_sobre, btn_saude, master)
    )
    btn_sobre.pack(side="left", padx=2, pady=2)
    
    btn_saude = ctk.CTkButton(
        tab_header, text="SAÚDE", width=120, corner_radius=25,
        fg_color="transparent", text_color="#64748B", hover_color="#E2E8F0",
        command=lambda: mudar_aba("saude", right_col, btn_sobre, btn_saude, master)
    )
    btn_saude.pack(side="left", padx=2, pady=2)

    container_abas = ctk.CTkFrame(right_col, fg_color="transparent")
    container_abas.pack(fill="both", expand=True, padx=40)
    
    mudar_aba("sobre", right_col, btn_sobre, btn_saude, master, container_abas)


def mudar_aba(aba, right_col, btn_sobre, btn_saude, master, container_abas=None):
    if container_abas is None:
        container_abas = right_col.children["!ctkframe2"]  # hack frágil – melhor passar sempre
    
    for w in container_abas.winfo_children():
        w.destroy()

    if aba == "sobre":
        btn_sobre.configure(fg_color="#14B8A6", text_color="white")
        btn_saude.configure(fg_color="transparent", text_color="#64748B")
        
        ctk.CTkLabel(container_abas, text="📝 Observações Gerais", font=("Arial", 16, "bold")).pack(anchor="w")
        txt = ctk.CTkTextbox(container_abas, fg_color="#F8FAFC", corner_radius=20, height=150, border_width=1, border_color="#E2E8F0")
        txt.pack(fill="x", pady=15)
        txt.insert("1.0", "Pet dócil, porém agitado em consultas. Histórico de alergia a certos medicamentos...")

        ctk.CTkLabel(container_abas, text="Comportamento", font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 10))
        tags = ["Brincalhão", "Curioso", "Agitado"]
        f_tags = ctk.CTkFrame(container_abas, fg_color="transparent")
        f_tags.pack(fill="x")
        for t in tags:
            ctk.CTkLabel(
                f_tags, text=t, fg_color="#F0FDFA", text_color="#14B8A6",
                corner_radius=15, padx=15, pady=5, font=("Arial", 11, "bold")
            ).pack(side="left", padx=5)

    else:  # saúde
        btn_saude.configure(fg_color="#14B8A6", text_color="white")
        btn_sobre.configure(fg_color="transparent", text_color="#64748B")
        
        h = ctk.CTkFrame(container_abas, fg_color="transparent")
        h.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(h, text="Protocolo de Vacinação", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(h, text="+ Novo Registro", fg_color="#14B8A6", width=120, corner_radius=20).pack(side="right")

        vacinas = [("V10", "10/01/2026", "10/01/2027"), ("Raiva", "15/12/2025", "15/12/2026")]
        for n, d, p in vacinas:
            v_card = ctk.CTkFrame(container_abas, fg_color="white", corner_radius=25, border_width=1, border_color="#F1F5F9")
            v_card.pack(fill="x", pady=10)
            ctk.CTkLabel(v_card, text="💉", font=("Arial", 25)).pack(side="left", padx=20, pady=20)
            ctk.CTkLabel(v_card, text=f"{n}\nAplicada: {d}", font=("Arial", 13, "bold"), justify="left").pack(side="left")
            ctk.CTkLabel(v_card, text=f"Reforço\n{p}", font=("Arial", 13, "bold"), text_color="#14B8A6", justify="right").pack(side="right", padx=20)