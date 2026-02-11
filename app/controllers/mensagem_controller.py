# src/controllers/mensagem_controller.py

from ..models.mensagens import (
    buscar_mensagens_conversa,
    salvar_mensagem,
    marcar_mensagens_como_lidas
)


class MensagemController:
    def __init__(self, usuario_id: str, usuario_tipo: str):
        """
        usuario_tipo: "TUTOR" ou "VETERINARIO"
        """
        self.usuario_id = usuario_id
        self.usuario_tipo = usuario_tipo.upper()

    def carregar_conversa(self, outro_usuario_id: str) -> dict:
        """
        Carrega todas as mensagens entre o usuário atual e o outro participante.
        """
        try:
            # Define quem é tutor e quem é veterinário na conversa
            if self.usuario_tipo == "TUTOR":
                id_tutor = self.usuario_id
                id_veterinario = outro_usuario_id
            else:
                id_tutor = outro_usuario_id
                id_veterinario = self.usuario_id

            mensagens = buscar_mensagens_conversa(id_tutor, id_veterinario)

            if not mensagens:
                return {
                    "success": True,
                    "message": "Nenhuma mensagem encontrada",
                    "mensagens": [],
                    "id_tutor": id_tutor,
                    "id_veterinario": id_veterinario
                }

            return {
                "success": True,
                "mensagens": mensagens,
                "id_tutor": id_tutor,
                "id_veterinario": id_veterinario
            }

        except Exception as e:
            return {
                "success": False,
                "message": "Erro ao carregar conversa",
                "error": str(e)
            }

    def enviar_mensagem(self, conteudo: str, destinatario_id: str) -> dict:
        """
        Envia (salva) uma nova mensagem.
        """
        try:
            if self.usuario_tipo == "TUTOR":
                id_tutor = self.usuario_id
                id_veterinario = destinatario_id
                enviado_por = "TUTOR"
            else:
                id_tutor = destinatario_id
                id_veterinario = self.usuario_id
                enviado_por = "VETERINARIO"

            if not conteudo.strip():
                return {
                    "success": False,
                    "message": "Mensagem vazia"
                }

            nova_msg = salvar_mensagem(
                conteudo=conteudo,
                enviado_por=enviado_por,
                id_tutor=id_tutor,
                id_veterinario=id_veterinario
            )

            if not nova_msg:
                return {
                    "success": False,
                    "message": "Falha ao salvar mensagem"
                }

            return {
                "success": True,
                "mensagem": nova_msg
            }

        except Exception as e:
            return {
                "success": False,
                "message": "Erro ao enviar mensagem",
                "error": str(e)
            }

    def marcar_conversa_como_lida(self, outro_usuario_id: str) -> dict:
        """
        Marca mensagens do outro usuário como lidas.
        """
        try:
            if self.usuario_tipo == "TUTOR":
                id_tutor = self.usuario_id
                id_veterinario = outro_usuario_id
            else:
                id_tutor = outro_usuario_id
                id_veterinario = self.usuario_id

            alteradas = marcar_mensagens_como_lidas(id_tutor, id_veterinario)

            return {
                "success": True,
                "marcadas_como_lidas": alteradas
            }

        except Exception as e:
            return {
                "success": False,
                "message": "Erro ao marcar como lidas",
                "error": str(e)
            }