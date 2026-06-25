import os

import customtkinter as ctk
from PIL import Image

import app.core.colors as colors
from app.core.i18n import tr


class LeftPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master,
            fg_color=colors.BRAND_DARK_TEAL,
            corner_radius=24,
        )

        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        base_dir = os.path.dirname(os.path.dirname(__file__))
        img_path = os.path.join(base_dir, "assets", "pet.png")

        pet_image = ctk.CTkImage(
            light_image=Image.open(img_path),
            dark_image=Image.open(img_path),
            size=(30, 30),
        )

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, padx=40, pady=30, sticky="w")

        ctk.CTkLabel(header_frame, image=pet_image, text="").grid(row=0, column=0, padx=(0, 8), sticky="w")
        header_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text=tr("Corações em Patas"),
            font=("Inter", 20, "bold"),
            text_color="white",
        ).grid(row=0, padx=40, pady=30, sticky="w")

        ctk.CTkLabel(
            self,
            text=tr("ÁREA DO VETERINÁRIO"),
            font=("Inter", 11, "bold"),
            fg_color=colors.TEXT_GRAY,
            corner_radius=10,
            text_color="white",
            padx=12,
            pady=4,
        ).grid(row=1, padx=40, sticky="w")

        ctk.CTkLabel(
            self,
            text=tr("Bem-vindo de\nvolta!"),
            font=("Inter", 36, "bold"),
            text_color="white",
            justify="left",
        ).grid(row=2, padx=50, sticky="w")

        ctk.CTkLabel(
            self,
            text=tr("Acompanhe a saúde emocional e física\ndo seu pet em um só lugar."),
            font=("Inter", 14),
            text_color="#E5D9FF",
            justify="left",
        ).grid(row=3, padx=40, pady=(0, 40), sticky="sw")
