# screens/config_gerais_screen.py
import customtkinter as ctk


def create_config_gerais_screen(master):
    scroll = ctk.CTkScrollableFrame(master, fg_color="transparent")
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

    c_dang = ctk.CTkFrame(scroll, fg_color="white", corner_radius=20, border_width=1, border_color="#FCA5A5")
    c_dang.pack(fill="x", pady=20)
    ctk.CTkLabel(c_dang, text="⚠️ Desativar conta", font=("Arial", 14, "bold"), text_color="#EF4444").pack(anchor="w", padx=20, pady=(15, 0))
    ctk.CTkLabel(c_dang, text="Essa ação não pode ser desfeita.", font=("Arial", 12)).pack(anchor="w", padx=20)
    ctk.CTkButton(c_dang, text="Desativar", fg_color="#EF4444", command=master.master.mostrar_modal).pack(anchor="w", padx=20, pady=15)