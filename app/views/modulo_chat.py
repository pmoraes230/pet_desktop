import customtkinter as ctk
import websocket
import json
import threading
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.services.s3_client import get_url_s3
import random

logger = logging.getLogger(__name__)

from ..controllers.tutor_controller import TutorController 
from ..controllers.mensagem_controller import MensagemController

class ModuloChat:
    def __init__(self, content_frame, current_user_id, current_user_role):
        self.content = content_frame
        
        self.current_user_id   = current_user_id
        self.current_user_role = current_user_role.upper()
        self.current_contact_id = None
        self.ws = None                    # WebSocket da conversa ativa
        self.ws_thread = None
        self.notif_ws = None              # WebSocket de notificações globais
        self.notif_thread = None
        self.msg_entry = None
        self.header_label = None
        self.pending_messages = []
        self.connection_ready = False
        self.scroll_contatos = None       # Referência para percorrer botões de contatos
        
        self.tutor_controller = None
        if self.current_user_role == "VETERINARIO":
            self.tutor_controller = TutorController(veterinario_id=self.current_user_id)

    def _criar_imagem_padrao_avatar(self, size=(48, 48)):
        inicial = "?"
        bg_color = random.choice(["#A855F7", "#EC4899", "#F59E0B", "#10B981", "#3B82F6"])

        img = Image.new("RGBA", size, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0) + size, fill=bg_color)

        try:
            font = ImageFont.truetype("arial.ttf", int(size[0] * 0.55))
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0,0), inicial, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size[0] - text_w) // 2
        y = (size[1] - text_h) // 2 - 2

        draw.text((x, y), inicial, font=font, fill="white")
        return img

    def tela_chat(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        chat_container = ctk.CTkFrame(self.content, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        chat_container.columnconfigure(0, weight=1)
        chat_container.columnconfigure(1, weight=3)
        chat_container.rowconfigure(0, weight=1)

        contatos_frame = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        contatos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(contatos_frame, text="Conversas", font=("Arial", 20, "bold")).pack(anchor="w", padx=25, pady=20)
        
        scroll_contatos = ctk.CTkScrollableFrame(contatos_frame, fg_color="transparent")
        scroll_contatos.pack(fill="both", expand=True, padx=10)
        self.scroll_contatos = scroll_contatos  # Guardamos para usar no destaque de novas mensagens

        # Janela de chat + header
        janela_chat = ctk.CTkFrame(chat_container, fg_color="white", corner_radius=25, border_width=1, border_color="#E2E8F0")
        janela_chat.grid(row=0, column=1, sticky="nsew")
        
        header = ctk.CTkFrame(janela_chat, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=15)
        
        self.header_label = ctk.CTkLabel(header, text="Selecione uma conversa", font=("Arial", 16, "bold"))
        self.header_label.pack(side="left")
        
        self.area_msg = ctk.CTkScrollableFrame(janela_chat, fg_color="#F8FAFC", corner_radius=0)
        self.area_msg.pack(fill="both", expand=True)
        
        input_f = ctk.CTkFrame(janela_chat, fg_color="white", height=80)
        input_f.pack(fill="x", side="bottom", padx=20, pady=20)
        
        self.msg_entry = ctk.CTkEntry(input_f, placeholder_text="Digite sua mensagem...", height=50, corner_radius=25)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.enviar_mensagem())

        ctk.CTkButton(input_f, text="➤", width=50, height=50, corner_radius=25, fg_color="#A855F7",
                      command=self.enviar_mensagem).pack(side="right")

        # Conecta notificações globais ANTES de carregar contatos
        self.conectar_notificacoes_globais()

        # Carrega lista de contatos
        self.carregar_lista_contatos(scroll_contatos)

    def conectar_notificacoes_globais(self):
        """Conecta WS persistente para receber mensagens de QUALQUER conversa em tempo real"""
        if self.notif_ws is not None:
            try:
                if self.notif_ws.sock and self.notif_ws.sock.connected:
                    return
            except:
                pass

        role_url = "vet" if self.current_user_role == "VETERINARIO" else "tutor"
        ws_url = f"wss://coracaoempatas.up.railway.app/ws/notificacoes/{role_url}/{self.current_user_id}/"

        def on_message(ws, raw_message):
            try:
                data = json.loads(raw_message)
                if data.get("tipo") != "nova_mensagem":
                    return

                conversa_com = data.get("conversa_com")
                if not conversa_com:
                    return

                if conversa_com == self.current_contact_id:
                    # Mensagem da conversa aberta → exibe na tela
                    tipo_bolha = "vet" if data["enviado_por"] == "VETERINARIO" else "tutor"
                    hora = data.get("data_envio", datetime.now().strftime("%H:%M"))
                    self.criar_bolha_mensagem(self.area_msg, data["mensagem"], hora, tipo_bolha)
                    self.area_msg._parent_canvas.yview_moveto(1.0)
                else:
                    # Mensagem de outra conversa → destaca o contato
                    self.mostrar_indicador_nova_mensagem(conversa_com)

            except json.JSONDecodeError:
                logger.debug("Mensagem de notificação inválida (não JSON)")
            except Exception as e:
                logger.error(f"Erro ao processar notificação: {e}")

        def on_open(ws):
            logger.info("[Notificações Globais] Conectado com sucesso")

        def on_error(ws, error):
            logger.warning(f"[Notificações Globais] Erro: {error}")

        def on_close(ws, close_code, close_msg):
            logger.info(f"[Notificações Globais] Fechado ({close_code}): {close_msg}")
            self.notif_ws = None
            # Opcional: reconexão automática simples
            # self.content.after(8000, self.conectar_notificacoes_globais)

        self.notif_ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.notif_thread = threading.Thread(
            target=self.notif_ws.run_forever,
            daemon=True,
            kwargs={"ping_interval": 30, "ping_timeout": 10}
        )
        self.notif_thread.start()

    def mostrar_indicador_nova_mensagem(self, contact_id):
        """Destaca o contato que recebeu nova mensagem (quando não está aberto)"""
        if not self.scroll_contatos:
            return

        for widget in self.scroll_contatos.winfo_children():
            if not isinstance(widget, ctk.CTkButton):
                continue

            # Melhor forma: se você adicionar btn.contact_id = contact_id ao criar o botão
            if hasattr(widget, 'contact_id') and widget.contact_id == contact_id:
                widget.configure(
                    fg_color="#E9D5FF",       # roxo claro
                    hover_color="#D8B4FE",
                    text_color="#6B21A8"
                )
                break

            # Alternativa menos confiável (se não tiver adicionado o atributo)
            # if contact_id in widget._text.strip():
            #     widget.configure(fg_color="#E9D5FF", hover_color="#D8B4FE")
            #     break

    def carregar_lista_contatos(self, scroll_frame):
        if self.current_user_role != "VETERINARIO" or not self.tutor_controller:
            ctk.CTkLabel(scroll_frame, text="Apenas veterinários acessam esta lista", text_color="gray").pack(pady=40)
            return

        contatos = self.tutor_controller.listar_contatos()

        if not contatos:
            ctk.CTkLabel(scroll_frame, text="Nenhum tutor encontrado", text_color="gray").pack(pady=40)
            return

        tutor_inicial = contatos[0]
        self.current_contact_id = tutor_inicial["id"]
        self.header_label.configure(text=f"Conversando com {tutor_inicial['nome']}")

        for contato in contatos:
            sel = (contato["id"] == self.current_contact_id)
            avatar_key = contato.get("imagem_perfil_tutor")
            
            btn = self.criar_item_contato(
                master=scroll_frame,
                nome=contato["nome"],
                avatar_key=avatar_key,
                sel=sel,
                contact_id=contato["id"]
            )
            
            # IMPORTANTE: adiciona atributo para facilitar identificação depois
            btn.contact_id = contato["id"]

        self.carregar_mensagens_iniciais(self.current_contact_id)

    def criar_item_contato(self, master, nome, avatar_key, sel=False, contact_id=None):
        AVATAR_SIZE = (48, 48)

        def criar_imagem_redonda(pil_img, size):
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            output = Image.new("RGBA", size)
            output.paste(pil_img, (0, 0), mask)
            return output

        if not avatar_key or avatar_key == '🐶' or len(avatar_key) < 5 or '/' not in avatar_key:
            pil_img = self._criar_imagem_padrao_avatar(size=AVATAR_SIZE)
        else:
            try:
                url = f"https://coracao-em-patas.s3.amazonaws.com/{avatar_key}"
                session = requests.Session()
                retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
                session.mount('https://', HTTPAdapter(max_retries=retries))
                response = session.get(url, timeout=8)
                response.raise_for_status()
                pil_img = Image.open(BytesIO(response.content)).convert("RGBA")
                pil_img = criar_imagem_redonda(pil_img, AVATAR_SIZE)
            except Exception as e:
                logger.warning(f"Erro ao carregar avatar {avatar_key}: {e}")
                pil_img = self._criar_imagem_padrao_avatar(size=AVATAR_SIZE)

        ctk_avatar = ctk.CTkImage(light_image=pil_img, size=AVATAR_SIZE)

        def on_click():
            for widget in self.area_msg.winfo_children():
                widget.destroy()
            self.conectar_websocket(contact_id, nome)

        btn = ctk.CTkButton(
            master=master,
            image=ctk_avatar,
            text=f"  {nome}",
            compound="left",
            fg_color="#F3E8FF" if sel else "transparent",
            text_color="black",
            hover_color="#F8FAFC",
            anchor="w",
            height=60,
            corner_radius=15,
            command=on_click
        )
        btn.pack(fill="x", pady=3, padx=5)
        return btn  # Retorna o botão para podermos adicionar .contact_id

    def carregar_mensagens_iniciais(self, tutor_id):
        for widget in self.area_msg.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(self.area_msg, text="Carregando mensagens...", text_color="gray")
        loading_label.pack(pady=20)
        self.area_msg.update()

        msg_ctrl = MensagemController(
            usuario_id=self.current_user_id,
            usuario_tipo=self.current_user_role
        )
        
        resultado = msg_ctrl.carregar_conversa(outro_usuario_id=tutor_id)
        
        loading_label.destroy()

        if resultado["success"] and resultado["mensagens"]:
            for msg in resultado["mensagens"]:
                texto = msg["CONTEUDO"]
                data_envio = msg.get("DATA_ENVIO")
                if isinstance(data_envio, datetime):
                    hora = data_envio.strftime("%H:%M")
                elif isinstance(data_envio, str):
                    try:
                        dt = datetime.fromisoformat(data_envio)
                        hora = dt.strftime("%H:%M")
                    except:
                        hora = data_envio[:5] if len(data_envio) >= 5 else "agora"
                else:
                    hora = "agora"

                enviado_por = msg["ENVIADO_POR"]
                tipo = "vet" if enviado_por == "VETERINARIO" else "tutor"
                
                self.criar_bolha_mensagem(self.area_msg, texto, hora, tipo)
            
            self.area_msg._parent_canvas.yview_moveto(1.0)
        else:
            ctk.CTkLabel(self.area_msg, text="Nenhuma mensagem ainda", text_color="gray").pack(pady=40)

    def criar_bolha_mensagem(self, master, texto, hora, tipo):
        if tipo == "vet":
            side = "right"
            bg_color = "#9333EA"
            text_color = "white"
            border_width = 0
        else:
            side = "left"
            bg_color = "white"
            text_color = "black"
            border_width = 1

        msg_frame = ctk.CTkFrame(master, fg_color="transparent")
        msg_frame.pack(fill="x", padx=15, pady=6)

        bolha_frame = ctk.CTkFrame(
            msg_frame,
            fg_color=bg_color,
            corner_radius=18,
            border_width=border_width,
            border_color="#E2E8F0"
        )
        bolha_frame.pack(side=side, padx=(0 if side == "right" else 10, 0 if side == "left" else 10))

        label_texto = ctk.CTkLabel(
            bolha_frame,
            text=texto,
            text_color=text_color,
            wraplength=280,
            justify="left",
            font=("Arial", 13)
        )
        label_texto.pack(padx=16, pady=(10, 6))

        label_hora = ctk.CTkLabel(
            msg_frame,
            text=hora,
            text_color="#94A3B8",
            font=("Arial", 10)
        )
        label_hora.pack(side=side, padx=5, pady=(0, 4))

        master._parent_canvas.yview_moveto(1.0)

    def conectar_websocket(self, contact_id, nome_contato):
        if self.current_contact_id == contact_id and self.ws and self.ws.sock.connected:
            return

        self.current_contact_id = contact_id
        self.header_label.configure(text=f"Conversando com {nome_contato}")

        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.debug(f"Erro ao fechar WS antigo: {e}")

        ws_url = f"wss://coracaoempatas.up.railway.app/ws/chat/{contact_id}/"

        def on_message(ws, raw_message):
            try:
                data = json.loads(raw_message)
                if "error" in data:
                    logger.error(f"Erro do servidor: {data['error']}")
                    return

                texto = data.get("mensagem")
                if not texto:
                    return

                enviado_por = data.get("enviado_por", "TUTOR")
                hora = data.get("data_envio", "agora")

                tipo = "vet" if enviado_por == "VETERINARIO" else "tutor"
                self.criar_bolha_mensagem(self.area_msg, texto, hora, tipo)
                self.area_msg._parent_canvas.yview_moveto(1.0)

            except json.JSONDecodeError:
                logger.error("Mensagem recebida inválida (não JSON)")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem recebida: {e}")

        def on_open(ws):
            auth_payload = {
                "user_id": str(self.current_user_id),
                "user_role": self.current_user_role.upper()
            }
            ws.send(json.dumps(auth_payload))
            logger.info(f"Autenticação enviada para {nome_contato}: {auth_payload}")

            self.connection_ready = True

            while self.pending_messages:
                pendente = self.pending_messages.pop(0)
                ws.send(json.dumps({"mensagem": pendente}))
                logger.info(f"Mensagem pendente enviada: {pendente}")

        def on_error(ws, error):
            logger.error(f"Erro WebSocket: {error}")
            self.connection_ready = False

        def on_close(ws, close_code, close_msg):
            logger.info(f"WebSocket fechado: código={close_code}, motivo={close_msg}")
            self.connection_ready = False
            self.ws = None

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()

    def enviar_mensagem(self):
        if not self.msg_entry:
            return

        texto = self.msg_entry.get().strip()
        if not texto:
            return

        meu_tipo = "vet" if self.current_user_role in ["VETERINARIO", "vet"] else "tutor"
        self.criar_bolha_mensagem(self.area_msg, texto, "agora", meu_tipo)
        self.area_msg._parent_canvas.yview_moveto(1.0)

        if self.ws and self.ws.sock and self.ws.sock.connected and self.connection_ready:
            self.ws.send(json.dumps({"mensagem": texto}))
        else:
            self.pending_messages.append(texto)
            logger.info("Mensagem enfileirada (conexão ainda não pronta)")

        self.msg_entry.delete(0, "end")

    def __del__(self):
        """Tenta fechar os websockets ao destruir o objeto"""
        try:
            if self.ws:
                self.ws.close()
        except:
            pass
        try:
            if self.notif_ws:
                self.notif_ws.close()
        except:
            pass