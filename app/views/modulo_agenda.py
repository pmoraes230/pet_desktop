import customtkinter as ctk

class ModuloAgenda:
    def __init__(self, content_frame):
        self.content = content_frame

    def tela_agenda(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Agendamentos", font=("Arial", 24, "bold")).pack(side="left")
        
        badge = ctk.CTkFrame(header, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="Fevereiro 2026", font=("Arial", 14, "bold")).pack(padx=20, pady=5)
        
        dias_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        dias_frame.pack(fill="x", pady=(0, 30))
        dias_frame.columnconfigure((0,1,2,3,4,5,6), weight=1)
        
        dias = [("seg", "10"), ("ter", "11"), ("qua", "12"), ("qui", "13"), ("sex", "14"), ("sáb", "15"), ("dom", "16")]
        for i, (nome, num) in enumerate(dias):
            d_card = ctk.CTkFrame(dias_frame, fg_color="transparent")
            d_card.grid(row=0, column=i, pady=20)
            ctk.CTkLabel(d_card, text=nome, font=("Arial", 13), text_color="#64748B").pack()
            ctk.CTkLabel(d_card, text=num, font=("Arial", 16, "bold")).pack()
        
        consultas = [
            ("08:00", "09:00", "Vacinação: Paçoca", "Dr. Silva . Sala 03"),
            ("09:00", "10:30", "Raio-X: Thor", "Dr. Helena . Sala 03")
        ]
        for hf, hp, tit, det in consultas:
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=10)
            ctk.CTkLabel(r, text=hf, font=("Arial", 16, "bold"), width=80).pack(side="left", padx=(0, 20))
            self.criar_card_agendamento_detalhado(r, hp, tit, det)

    def criar_card_agendamento_detalhado(self, master, hora, tit, sub):
        c = ctk.CTkFrame(master, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        c.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(c, text="🕒", font=("Arial", 18)).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(c, text=hora, font=("Arial", 16, "bold")).pack(side="left")
        t = ctk.CTkFrame(c, fg_color="transparent")
        t.pack(side="left", padx=20, fill="x", expand=True)
        ctk.CTkLabel(t, text=tit, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(t, text=sub, font=("Arial", 11), text_color="#64748B").pack(anchor="w")