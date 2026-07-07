from datetime import datetime
from io import BytesIO

import customtkinter as ctk
import requests
import tkinter as tk
from PIL import Image, ImageDraw

from app.controllers.perfil_controller import FotoPerfil
from app.core.i18n import tr
from app.core.theme import is_dark_mode
from app.services.realtime_client import RealtimeClient
from app.services.s3_client import get_url_s3


class Colors:
    ACCENT = "#9333EA"
    ACCENT_SOFT = "#F3E8FF"

    def __init__(self):
        self.apply_appearance()

    def apply_appearance(self):
        if is_dark_mode():
            self.BG = "#111827"
            self.CARD_BG = "#1F2937"
            self.PANEL_BG = "#111827"
            self.BORDER = "#374151"
            self.TEXT = "#F9FAFB"
            self.TEXT_MUTED = "#9CA3AF"
            self.SELECTED = "#3B0764"
            self.HOVER = "#374151"
            self.BUBBLE_OTHER = "#111827"
            return

        self.BG = "#F8FAFC"
        self.CARD_BG = "#FFFFFF"
        self.PANEL_BG = "#F8FAFC"
        self.BORDER = "#E2E8F0"
        self.TEXT = "#111827"
        self.TEXT_MUTED = "#64748B"
        self.SELECTED = "#F3E8FF"
        self.HOVER = "#F8FAFC"
        self.BUBBLE_OTHER = "#FFFFFF"


colors = Colors()


class ModuloChat:
    def __init__(self, content_frame, current_user=None):
        self.content = content_frame
        self.current_user = current_user or {}
        self.current_user_id = self.current_user.get("id")
        self.channel = f"veterinario:{self.current_user_id}" if self.current_user_id else None
        self.realtime = None
        self.area_msg = None
        self.input_msg = None
        self.status_label = None
        self.header_avatar = None
        self.header_name_label = None
        self.profile_name = None
        self.profile_photo_key = None
        self._carregar_dados_perfil()

    def tela_chat(self):
        colors.apply_appearance()
        self.content.configure(fg_color=colors.BG)
        self._fechar_tempo_real()

        for widget in self.content.winfo_children():
            widget.destroy()

        chat_container = ctk.CTkFrame(self.content, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        chat_container.columnconfigure(0, weight=1)
        chat_container.columnconfigure(1, weight=3)
        chat_container.rowconfigure(0, weight=1)

        contatos_frame = ctk.CTkFrame(chat_container, fg_color=colors.CARD_BG, corner_radius=25, border_width=1, border_color=colors.BORDER)
        contatos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(contatos_frame, text=tr("Conversas"), font=("Arial", 20, "bold"), text_color=colors.TEXT).pack(anchor="w", padx=25, pady=20)

        scroll_contatos = ctk.CTkScrollableFrame(contatos_frame, fg_color="transparent")
        scroll_contatos.pack(fill="both", expand=True, padx=10)

        self.criar_item_contato(scroll_contatos, "Canal do veterinario", "Vet", True)

        janela_chat = ctk.CTkFrame(chat_container, fg_color=colors.CARD_BG, corner_radius=25, border_width=1, border_color=colors.BORDER)
        janela_chat.grid(row=0, column=1, sticky="nsew")

        header = ctk.CTkFrame(janela_chat, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=15)

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        self.header_avatar = ctk.CTkLabel(left_header, text="👤", width=38, height=38, corner_radius=19, fg_color="#E5E7EB")
        self.header_avatar.pack(side="left")

        self.header_name_label = ctk.CTkLabel(
            left_header,
            text=self._obter_nome_header(),
            font=("Arial", 16, "bold"),
            text_color=colors.TEXT,
        )
        self.header_name_label.pack(side="left", padx=(10, 0))

        self.status_label = ctk.CTkLabel(header, text="Conectando...", font=("Arial", 12), text_color=colors.TEXT_MUTED)
        self.status_label.pack(side="right")

        self.content.after(150, self._carregar_avatar_header)

        self.area_msg = ctk.CTkScrollableFrame(janela_chat, fg_color=colors.PANEL_BG, corner_radius=0)
        self.area_msg.pack(fill="both", expand=True)

        input_f = ctk.CTkFrame(janela_chat, fg_color=colors.CARD_BG, height=80)
        input_f.pack(fill="x", side="bottom", padx=20, pady=20)
        self.input_msg = ctk.CTkEntry(input_f, placeholder_text=tr("Digite sua mensagem..."), height=50, corner_radius=25, fg_color=colors.PANEL_BG, border_color=colors.BORDER, text_color=colors.TEXT, placeholder_text_color=colors.TEXT_MUTED)
        self.input_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_msg.bind("<Return>", lambda _event: self.enviar_mensagem())
        ctk.CTkButton(input_f, text="Enviar", width=90, height=50, corner_radius=25, fg_color="#A855F7", command=self.enviar_mensagem).pack(side="right")

        self._abrir_tempo_real()

    def _abrir_tempo_real(self):
        if not self.channel:
            self._atualizar_status("Usuario sem canal de tempo real.")
            return

        self.realtime = RealtimeClient(
            on_message=lambda message: self._agendar_ui(self._receber_mensagem, message),
            on_status=lambda status: self._agendar_ui(self._atualizar_status, status),
            user_id=self.current_user_id,
            role="veterinario",
        )
        self.realtime.connect([self.channel])

    def _fechar_tempo_real(self):
        if self.realtime:
            self.realtime.close()
            self.realtime = None

    def enviar_mensagem(self):
        texto = self.input_msg.get().strip() if self.input_msg else ""
        if not texto or not self.realtime or not self.channel:
            return

        payload = {
            "texto": texto,
            "origem": "desktop",
            "sender_id": self.current_user_id,
        }

        try:
            self.realtime.publish(self.channel, "mensagem_chat", payload)
            self.input_msg.delete(0, "end")
        except Exception as exc:
            self._atualizar_status(f"Falha ao enviar: {exc}")

    def _agendar_ui(self, callback, *args):
        try:
            if not self.content or not self.content.winfo_exists():
                return
            self.content.after(0, lambda: self._executar_ui(callback, *args))
        except tk.TclError:
            pass

    def _executar_ui(self, callback, *args):
        try:
            if not self.content or not self.content.winfo_exists():
                return
            callback(*args)
        except (tk.TclError, RuntimeError):
            pass

    def _receber_mensagem(self, message):
        event = message.get("event")
        if event in {"connected", "subscribed"}:
            return

        payload = message.get("payload") or {}
        texto = payload.get("texto") or payload.get("message") or payload.get("mensagem")
        if not texto:
            return

        origem = payload.get("origem")
        tipo = "vet" if origem == "desktop" else "tutor"
        if self.area_msg and self.area_msg.winfo_exists():
            self.criar_bolha_mensagem(self.area_msg, texto, self._hora_atual(), tipo)

    def _atualizar_status(self, texto):
        if self.status_label:
            try:
                if self.status_label.winfo_exists():
                    self.status_label.configure(text=texto)
            except tk.TclError:
                pass

    def _carregar_dados_perfil(self):
        user_id = self.current_user.get("id") or self.current_user.get("ID") or self.current_user.get("veterinario_id")
        if not user_id:
            return

        try:
            foto_perfil = FotoPerfil(user_id)
            dados = foto_perfil.fetch_perfil_data()
            if dados:
                self.profile_name = dados.get("NOME") or dados.get("nome") or self.current_user.get("name") or self.current_user.get("nome") or "Usuário"
                self.profile_photo_key = dados.get("imagem_perfil_veterinario")
        except Exception as exc:
            print(f"Falha ao carregar perfil do chat: {exc}")

    def _obter_nome_header(self):
        return self.profile_name or self.current_user.get("name") or self.current_user.get("nome") or tr("Tempo real")

    def _carregar_avatar_header(self):
        if not self.header_avatar or not self.profile_photo_key:
            return

        try:
            url = get_url_s3(self.profile_photo_key, expires_in=604800)
            if not url:
                return

            response = requests.get(url, timeout=6)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize((38, 38))

            mask = Image.new("L", (38, 38), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 37, 37), fill=255)

            output = Image.new("RGBA", (38, 38), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            img_ctk = ctk.CTkImage(light_image=output, size=(38, 38))

            self.header_avatar.configure(image=img_ctk, text="")
            self.header_avatar.image = img_ctk
        except Exception as exc:
            print(f"Falha ao carregar avatar do header: {exc}")
            if self.header_avatar.winfo_exists():
                self.header_avatar.configure(text="👤", image=None)

    def criar_item_contato(self, master, nome, avatar, sel=False):
        btn = ctk.CTkButton(
            master,
            text=f"{avatar}  {nome}",
            fg_color=colors.SELECTED if sel else "transparent",
            text_color=colors.TEXT,
            hover_color=colors.HOVER,
            anchor="w",
            height=60,
            corner_radius=15,
        )
        btn.pack(fill="x", pady=2)

    def criar_bolha_mensagem(self, master, texto, hora, tipo):
        side = "right" if tipo == "vet" else "left"
        cor = colors.ACCENT if tipo == "vet" else colors.BUBBLE_OTHER
        txt_cor = "white" if tipo == "vet" else colors.TEXT
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=5)
        bolha = ctk.CTkFrame(f, fg_color=cor, corner_radius=15, border_width=1 if tipo == "tutor" else 0, border_color=colors.BORDER)
        bolha.pack(side=side)
        ctk.CTkLabel(bolha, text=texto, text_color=txt_cor, wraplength=250, justify="left").pack(padx=15, pady=10)
        ctk.CTkLabel(f, text=hora, font=("Arial", 9), text_color=colors.TEXT_MUTED).pack(side=side, padx=5)

    def _hora_atual(self):
        return datetime.now().strftime("%H:%M")
