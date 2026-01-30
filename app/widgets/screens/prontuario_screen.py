# screens/prontuario_screen.py
import customtkinter as ctk


def create_prontuario_screen(master):
    container = ctk.CTkFrame(master, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=30, pady=20)

    header = ctk.CTkFrame(container, fg_color="transparent")
    header.pack(fill="x", pady=(0, 20))

    left_header = ctk.CTkFrame(header, fg_color="transparent")
    left_header.pack(side="left", fill="x", expand=True)

    ctk.CTkLabel(left_header, text="Prontuário eletrônico", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 10))

    search_row = ctk.CTkFrame(left_header, fg_color="transparent")
    search_row.pack(fill="x", anchor="w")
    
    ctk.CTkEntry(
        search_row, 
        placeholder_text="🔍 Pesquise por tutor ou pet (ex: Thor, Luna...)", 
        height=45, width=400, corner_radius=22, border_color="#94A3B8"
    ).pack(side="left")

    ctk.CTkButton(
        header, 
        text="Salvar prontuário", 
        fg_color="#A855F7", hover_color="#9333EA",
        font=("Arial", 14, "bold"), width=180, height=45, corner_radius=10
    ).pack(side="right", anchor="n")

    corpo = ctk.CTkFrame(container, fg_color="transparent")
    corpo.pack(fill="both", expand=True)
    corpo.columnconfigure(0, weight=3)
    corpo.columnconfigure(1, weight=1)

    editor = ctk.CTkFrame(corpo, fg_color="transparent")
    editor.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
    
    ctk.CTkLabel(editor, text="Anotações", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
    
    txt = ctk.CTkTextbox(
        editor, corner_radius=20, border_width=1, border_color="#94A3B8", 
        fg_color="#E5E7EB", text_color="black", font=("Arial", 13)
    )
    txt.pack(fill="both", expand=True)
    txt.insert("1.0", "Digite aqui as observações...")

    hist = ctk.CTkFrame(corpo, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
    hist.grid(row=0, column=1, sticky="nsew")
    
    ctk.CTkLabel(hist, text="Histórico Recente", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))

    scroll_h = ctk.CTkScrollableFrame(hist, fg_color="transparent")
    scroll_h.pack(fill="both", expand=True, padx=10, pady=15)
    
    master.master.criar_item_historico(scroll_h, "15 Jan 2026", "Vacinação")
    master.master.criar_item_historico(scroll_h, "02 Dez 2025", "Check-up Geral")