import asyncio
import json
import logging
import os
from typing import Dict, Callable, Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisChatManager:
    """
    Gerenciador de Pub/Sub para salas de chat usando Redis.
    Usa duas conexões separadas (publish e subscribe) para maior estabilidade.
    """

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        if not self.redis_url:
            raise ValueError("REDIS_URL não encontrado nas variáveis de ambiente!")

        logger.info("RedisChatManager inicializado com URL: %s", self.redis_url)

        self._pub_client: redis.Redis | None = None
        self._sub_client: redis.Redis | None = None
        self._pubsub: redis.PubSub | None = None

        # room_name → (task de listener, conjunto de callbacks)
        self._subscriptions: Dict[str, tuple[asyncio.Task, set[Callable]]] = {}

    async def connect(self, max_retries: int = 5, retry_delay: float = 3.0) -> None:
        """Estabelece conexões com Redis com retry automático"""
        if self._pub_client and self._sub_client:
            return

        for attempt in range(1, max_retries + 1):
            try:
                common_config = {
                    "decode_responses": True,
                    "socket_timeout": 5.0,
                    "socket_connect_timeout": 5.0,
                    "retry_on_timeout": True,
                    "health_check_interval": 30,
                    "max_connections": 20,
                }

                self._pub_client = await redis.from_url(self.redis_url, **common_config)
                self._sub_client = await redis.from_url(self.redis_url, **common_config)
                self._pubsub = self._sub_client.pubsub()

                await self._pub_client.ping()
                await self._sub_client.ping()

                logger.info("Conexões Redis estabelecidas com sucesso")
                return

            except redis.RedisError as e:
                logger.warning(f"Tentativa {attempt}/{max_retries} falhou: {e}")
                if attempt == max_retries:
                    logger.critical("Falha definitiva ao conectar ao Redis após %d tentativas", max_retries)
                    raise
                await asyncio.sleep(retry_delay * (1.5 ** (attempt - 1)))  # backoff exponencial

        raise RuntimeError("Não foi possível conectar ao Redis após várias tentativas")

    async def close(self) -> None:
        """Fecha todas as conexões e cancela listeners"""
        try:
            for task, _ in self._subscriptions.values():
                task.cancel()

            await asyncio.gather(
                *[t for t, _ in self._subscriptions.values() if not t.done()],
                return_exceptions=True
            )

            self._subscriptions.clear()

            if self._pubsub:
                await self._pubsub.close()
            if self._pub_client:
                await self._pub_client.aclose()
            if self._sub_client:
                await self._sub_client.aclose()

            logger.info("RedisChatManager fechado com sucesso")

        except Exception as e:
            logger.warning("Erro ao fechar conexões Redis: %s", e)

    async def subscribe(self, channel: str, callback: Callable[[dict], Any]) -> None:
        """
        Inscreve um callback em um canal (room).
        Múltiplos callbacks podem ser registrados no mesmo canal.
        """
        if not self._pubsub:
            await self.connect()

        if channel not in self._subscriptions:
            async def listener():
                while True:
                    try:
                        await self._pubsub.subscribe(channel)
                        logger.debug("Escutando canal: %s", channel)
                        async for msg in self._pubsub.listen():
                            if msg.get("type") == "message":
                                try:
                                    data = json.loads(msg["data"])
                                    for cb in list(self._subscriptions[channel][1]):
                                        asyncio.create_task(cb(data))  # sem await → não bloqueia
                                except json.JSONDecodeError:
                                    logger.warning("JSON inválido no canal %s", channel)
                                except Exception as e:
                                    logger.error("Erro ao processar mensagem no canal %s: %s", channel, e, exc_info=True)
                    except redis.ConnectionError as e:
                        logger.warning("Conexão perdida em %s: %s → reconectando", channel, e)
                        await self.connect()
                        await asyncio.sleep(1)
                    except redis.RedisError as e:
                        logger.error("Erro Redis no listener %s: %s", channel, e)
                        await asyncio.sleep(3)
                    except asyncio.CancelledError:
                        logger.debug("Listener %s cancelado", channel)
                        break
                    except Exception as e:
                        logger.critical("Erro inesperado no listener %s: %s", channel, e, exc_info=True)
                        await asyncio.sleep(5)

            task = asyncio.create_task(listener())
            self._subscriptions[channel] = (task, set())

        # Adiciona o callback
        self._subscriptions[channel][1].add(callback)
        logger.debug("Callback adicionado em %s (total: %d)", channel, len(self._subscriptions[channel][1]))

    async def unsubscribe(self, channel: str, callback: Callable[[dict], Any] | None = None) -> None:
        """Remove um callback específico ou todos de um canal"""
        if channel not in self._subscriptions:
            return

        if callback:
            self._subscriptions[channel][1].discard(callback)
            if self._subscriptions[channel][1]:
                return  # ainda tem callbacks → mantém listener

        # Remove tudo
        task, _ = self._subscriptions.pop(channel)
        task.cancel()
        try:
            await self._pubsub.unsubscribe(channel)
            logger.debug("Canal %s desinscrito completamente", channel)
        except Exception as e:
            logger.debug(f"Erro ao unsubscribe do canal {channel}: {e}")

    async def publish(self, channel: str, message: dict) -> None:
        """Publica uma mensagem no canal"""
        if not self._pub_client:
            await self.connect()

        for attempt in range(1, 4):
            try:
                await self._pub_client.publish(channel, json.dumps(message))
                logger.debug("Mensagem publicada no canal %s", channel)
                return
            except redis.RedisError as e:
                logger.warning(f"Falha ao publicar (tentativa {attempt}): {e}")
                await asyncio.sleep(1)

        logger.error(f"Falha definitiva ao publicar no canal {channel}")


# Singleton recomendado
redis_manager = RedisChatManager()