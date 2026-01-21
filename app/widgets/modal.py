# app/widgets/modal.py
import customtkinter as ctk
import app.core.colors as colors
from typing import Literal

class Modal(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, type: Literal["success", "error", "info", "warning"] = "info"):
        super().__init__(master)
        self.title("")  # Remove título padrão da janela
        self.overrideredirect(True)  # Remove barra de título (dá visual mais "modal moderno")
        self.attributes("-topmost", True)  # Sempre no topo
        self.transient(master)
        self.grab_set()

        self.configure(fg_color=colors.TEXT_GRAY)  # Quase preto (evita erro de transparent)

        # Tamanho fixo como no seu HTML (max-w-sm ≈ 384px)
        width, height = 384, 240
        self.geometry(f"{width}x{height}")

        # Centraliza perfeitamente em relação à janela principal
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - width) // 2
        y = master.winfo_rooty() + (master.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self._build_ui(title, message, type)

        self.bind("<Escape>", lambda e: self.destroy())
        self.after(100, self.lift)  # Garante que fique acima de tudo

    def _build_ui(self, title, message, type_):
        # Backdrop simulada (frame que cobre tudo com cor escura semi-transparente)
        backdrop = ctk.CTkFrame(self, fg_color=colors.TEXT_GRAY, corner_radius=0)
        backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Card principal (branco, rounded-2xl, shadow simulada)
        card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=24,           # rounded-2xl ≈ 1.5rem = 24px
            border_width=1,
            border_color="#e5e7eb",
        )
        card.place(relx=0.5, rely=0.5, relwidth=0.92, relheight=0.88, anchor="center")

        # Sombra forte (simulada com frame extra maior e mais escuro)
        shadow = ctk.CTkFrame(self, fg_color=colors.TEXT_GRAY, corner_radius=28)
        shadow.place(relx=0.5, rely=0.5, relwidth=0.94, relheight=0.90, anchor="center")
        shadow.lower(card)  # Coloca atrás do card

        # Conteúdo interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=24)

        # Linha superior: ícone + textos
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        # Ícone circular
        icon_colors = {
            "success": "#10b981",  # green-500
            "error":   "#ef4444",  # red-500
            "info":    "#3b82f6",  # blue-500
            "warning": "#f59e0b",  # amber-500
        }
        icon_bg = icon_colors.get(type_, "#6b7280")
        icon_text = {"success": "✓", "error": "✕", "info": "i", "warning": "!"}.get(type_, "?")

        icon_frame = ctk.CTkFrame(header, fg_color=icon_bg, width=48, height=48, corner_radius=999)
        icon_frame.pack(side="left")
        ctk.CTkLabel(icon_frame, text=icon_text, text_color="white",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(expand=True)

        # Textos
        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", padx=16, fill="x", expand=True)

        ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#111827", anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_frame, text=message, font=ctk.CTkFont(size=14),
                     text_color="#4b5563", wraplength=260, justify="left").pack(anchor="w", pady=(4,0))

        # Botões à direita (como no HTML)
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(20,0))

        ctk.CTkButton(btn_frame, text="Fechar", width=100, height=42,
                      fg_color="#e5e7eb", hover_color="#d1d5db",
                      text_color="#374151", corner_radius=12,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.destroy).pack(side="right", padx=(12,0))

        brand_color = "#7c3aed"  # ajuste para o seu brand-purple
        ctk.CTkButton(btn_frame, text="OK", width=100, height=42,
                      fg_color=brand_color, hover_color="#6d28d9",
                      corner_radius=12,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.destroy).pack(side="right")

        # Pequena animação de entrada (scale + fade)
        card.configure(width=300)  # começa menor
        self.after(10, lambda: card.configure(width=360))