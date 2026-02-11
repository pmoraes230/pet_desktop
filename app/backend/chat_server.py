import asyncio
import json
import logging
from datetime import datetime
from websockets.server import serve, WebSocketServerProtocol

from .chat_manager_redis import RedisChatManager
from ..controllers.mensagem_controller import MensagemController

logger = logging.getLogger("chat_server")

manager = RedisChatManager()

connected_clients = {}  # websocket → {"user_id": ..., "room_name": ...}

async def chat_handler(websocket: WebSocketServerProtocol, path: str):
    parts = path.strip("/").split("/")
    if len(parts) < 2 or parts[0] != "chat":
        await websocket.close(1008, "Caminho inválido")
        return

    contact_id = parts[1]

    # 1. Autenticação inicial
    try:
        init_msg = await asyncio.wait_for(websocket.recv(), timeout=8.0)
        data = json.loads(init_msg)
        user_id = data.get("user_id")
        user_role = data.get("user_role", "")

        # Normaliza o role recebido (resolve o problema principal!)
        user_role_norm = user_role.upper() if user_role else ""
        valid_roles = ["TUTOR", "VETERINARIO", "VET"]
        
        if not user_id or user_role_norm not in valid_roles:
            logger.warning(f"Autenticação falhou - user_id={user_id}, role_recebido='{user_role}'")
            await websocket.send(json.dumps({"error": "Autenticação inválida - role inválido"}))
            await websocket.close(1008, "Autenticação inválida")
            return

        # Padroniza o role para uso interno
        if user_role_norm == "VET":
            user_role = "VETERINARIO"
        else:
            user_role = user_role_norm.lower() if user_role_norm == "TUTOR" else user_role_norm

        logger.info(f"Autenticação OK - user_id={user_id}, role={user_role} (original: {user_role})")

    except asyncio.TimeoutError:
        await websocket.close(1008, "Tempo de autenticação expirado")
        return
    except json.JSONDecodeError:
        await websocket.send(json.dumps({"error": "Formato de autenticação inválido"}))
        await websocket.close(1008)
        return
    except Exception as e:
        logger.error(f"Falha na autenticação: {e}", exc_info=True)
        await websocket.close(1008, "Erro interno na autenticação")
        return

    # 2. Cria controller
    controller = MensagemController(usuario_id=user_id, usuario_tipo=user_role)

    # 3. Room name (corrigido com sorted)
    ids_sorted = sorted([str(user_id), str(contact_id)])
    room_name = f"chat_{ids_sorted[0]}_{ids_sorted[1]}"

    # 4. Substitui conexão antiga do mesmo usuário na mesma sala (evita rejeição em reconexão)
    existing_ws = None
    for ws_conn, info in list(connected_clients.items()):
        if info.get("user_id") == user_id and info.get("room_name") == room_name:
            existing_ws = ws_conn
            break

    if existing_ws:
        try:
            if existing_ws.open:
                await existing_ws.close(1000, "Conexão substituída por nova sessão")
            logger.info(f"Conexão antiga substituída para {user_id} em {room_name}")
        except Exception as e:
            logger.debug(f"Erro ao fechar conexão antiga: {e}")
        finally:
            if existing_ws in connected_clients:
                del connected_clients[existing_ws]

    # Registra a nova conexão
    connected_clients[websocket] = {"user_id": user_id, "room_name": room_name}

    # 5. Callback de mensagens do Redis
    async def on_room_message(data):
        if websocket in connected_clients and connected_clients[websocket]["room_name"] == room_name:
            try:
                await websocket.send(json.dumps(data))
            except Exception as send_err:
                logger.debug(f"Erro ao enviar mensagem para client: {send_err}")

    await manager.subscribe(room_name, on_room_message)

    logger.info(f"[{user_role.upper()}] {user_id} conectado à sala {room_name}")

    # 6. Carrega histórico
    try:
        resultado = controller.carregar_conversa(outro_usuario_id=contact_id)

        if resultado.get("success") and isinstance(resultado.get("mensagens"), list):
            for msg in resultado["mensagens"]:
                data_envio = msg.get("DATA_ENVIO")
                hora_formatada = "agora"
                if isinstance(data_envio, datetime):
                    hora_formatada = data_envio.strftime("%H:%M")
                elif isinstance(data_envio, str):
                    try:
                        dt = datetime.fromisoformat(data_envio)
                        hora_formatada = dt.strftime("%H:%M")
                    except:
                        hora_formatada = data_envio[:5] if len(data_envio) >= 5 else "agora"

                sender_id = msg["ID_TUTOR"] if msg["ENVIADO_POR"] == "TUTOR" else msg["ID_VETERINARIO"]

                await websocket.send(json.dumps({
                    "mensagem": msg["CONTEUDO"],
                    "sender_id": str(sender_id),
                    "enviado_por": msg["ENVIADO_POR"],
                    "data_envio": hora_formatada,
                }))
        else:
            logger.info(f"Nenhuma mensagem histórica para {room_name}")
    except Exception as hist_err:
        logger.error(f"Erro ao carregar histórico para {room_name}: {hist_err}", exc_info=True)

    # Marca como lida (opcional)
    try:
        controller.marcar_conversa_como_lida(outro_usuario_id=contact_id)
    except Exception as mark_err:
        logger.warning(f"Erro ao marcar como lida: {mark_err}")

    # 7. Loop principal de mensagens recebidas
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                conteudo = data.get("mensagem")
                if not conteudo or not conteudo.strip():
                    continue

                resposta = controller.enviar_mensagem(
                    conteudo=conteudo,
                    destinatario_id=contact_id
                )

                if resposta.get("success") and resposta.get("mensagem"):
                    nova_msg = resposta["mensagem"]

                    data_envio = nova_msg.get("DATA_ENVIO")
                    hora_formatada = "agora"
                    if isinstance(data_envio, datetime):
                        hora_formatada = data_envio.strftime("%H:%M")
                    elif isinstance(data_envio, str):
                        try:
                            dt = datetime.fromisoformat(data_envio)
                            hora_formatada = dt.strftime("%H:%M")
                        except:
                            pass

                    payload = {
                        "mensagem": nova_msg["CONTEUDO"],
                        "sender_id": str(user_id),
                        "enviado_por": nova_msg["ENVIADO_POR"],
                        "data_envio": hora_formatada,
                    }

                    await manager.publish(room_name, payload)
                else:
                    await websocket.send(json.dumps({"error": "Falha ao salvar mensagem"}))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Formato JSON inválido"}))
            except Exception as msg_err:
                logger.error(f"Erro ao processar mensagem recebida: {msg_err}", exc_info=True)
                await websocket.send(json.dumps({"error": "Erro interno ao processar"}))

    except Exception as conn_err:
        logger.info(f"Conexão encerrada: {conn_err}")
    finally:
        try:
            if websocket in connected_clients:
                del connected_clients[websocket]
            await manager.unsubscribe(room_name, on_room_message)
            logger.info(f"[{user_role.upper()}] {user_id} desconectado da sala {room_name}")
        except Exception as cleanup_err:
            logger.warning(f"Erro no cleanup final: {cleanup_err}")

async def start_chat_server(host: str = "127.0.0.1", port: int = 8765):
    """
    Função principal para iniciar o servidor WebSocket + Redis.
    Chame essa função no seu main.py ou em um script de inicialização.
    """
    try:
        await manager.connect()  # Conecta ao Redis
        logger.info(f"Iniciando servidor WebSocket em ws://{host}:{port}")

        async with serve(chat_handler, host, port):
            logger.info("✅ Servidor WebSocket rodando com sucesso!")
            await asyncio.Future()  # Mantém o servidor rodando para sempre

    except Exception as e:
        logger.error(f"❌ Falha ao iniciar o servidor WebSocket: {e}", exc_info=True)
        raise