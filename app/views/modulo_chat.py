from datetime import datetime

import customtkinter as ctk

from app.core.i18n import tr
from app.services.realtime_client import RealtimeClient


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

    def tela_chat(self):
        self._fechar_tempo_real()

        for widget in self.content.winfo_children():
            widget.destroy()

        chat_container = ctk.CTkFrame(self.content, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        chat_container.columnconfigure(0, weight=1)
        chat_container.columnconfigure(1, weight=3)
        chat_container.rowconfigure(0, weight=1)

        contatos_frame = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        contatos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(contatos_frame, text=tr("Conversas"), font=("Arial", 20, "bold")).pack(anchor="w", padx=25, pady=20)

        scroll_contatos = ctk.CTkScrollableFrame(contatos_frame, fg_color="transparent")
        scroll_contatos.pack(fill="both", expand=True, padx=10)

        self.criar_item_contato(scroll_contatos, "Canal do veterinario", "Vet", True)

        janela_chat = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        janela_chat.grid(row=0, column=1, sticky="nsew")

        header = ctk.CTkFrame(janela_chat, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(header, text=tr("Tempo real"), font=("Arial", 16, "bold")).pack(side="left")
        self.status_label = ctk.CTkLabel(header, text="Conectando...", font=("Arial", 12), text_color="#64748B")
        self.status_label.pack(side="right")

        self.area_msg = ctk.CTkScrollableFrame(janela_chat, fg_color="#F8FAFC", corner_radius=0)
        self.area_msg.pack(fill="both", expand=True)

        input_f = ctk.CTkFrame(janela_chat, fg_color="white", height=80)
        input_f.pack(fill="x", side="bottom", padx=20, pady=20)
        self.input_msg = ctk.CTkEntry(input_f, placeholder_text=tr("Digite sua mensagem..."), height=50, corner_radius=25)
        self.input_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_msg.bind("<Return>", lambda _event: self.enviar_mensagem())
        ctk.CTkButton(input_f, text="Enviar", width=90, height=50, corner_radius=25, fg_color="#A855F7", command=self.enviar_mensagem).pack(side="right")

        self._abrir_tempo_real()

    def _abrir_tempo_real(self):
        if not self.channel:
            self._atualizar_status("Usuario sem canal de tempo real.")
            return

        self.realtime = RealtimeClient(
            on_message=lambda message: self.content.after(0, lambda: self._receber_mensagem(message)),
            on_status=lambda status: self.content.after(0, lambda: self._atualizar_status(status)),
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
        self.criar_bolha_mensagem(self.area_msg, texto, self._hora_atual(), tipo)

    def _atualizar_status(self, texto):
        if self.status_label:
            self.status_label.configure(text=texto)

    def criar_item_contato(self, master, nome, avatar, sel=False):
        btn = ctk.CTkButton(
            master,
            text=f"{avatar}  {nome}",
            fg_color="#F3E8FF" if sel else "transparent",
            text_color="black",
            hover_color="#F8FAFC",
            anchor="w",
            height=60,
            corner_radius=15,
        )
        btn.pack(fill="x", pady=2)

    def criar_bolha_mensagem(self, master, texto, hora, tipo):
        side = "right" if tipo == "vet" else "left"
        cor = "#9333EA" if tipo == "vet" else "white"
        txt_cor = "white" if tipo == "vet" else "black"
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=5)
        bolha = ctk.CTkFrame(f, fg_color=cor, corner_radius=15, border_width=1 if tipo == "tutor" else 0, border_color="#E2E8F0")
        bolha.pack(side=side)
        ctk.CTkLabel(bolha, text=texto, text_color=txt_cor, wraplength=250, justify="left").pack(padx=15, pady=10)
        ctk.CTkLabel(f, text=hora, font=("Arial", 9), text_color="#94A3B8").pack(side=side, padx=5)

    def _hora_atual(self):
        return datetime.now().strftime("%H:%M")
