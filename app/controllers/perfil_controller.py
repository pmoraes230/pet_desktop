from ..models.perfil_modal import PerfilModal


class FotoPerfil:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.perfil_modal = PerfilModal(user_id)

    def fetch_perfil_data(self) -> dict:
        """Recupera os dados do perfil do usuário"""
        return self.perfil_modal.get_perfil_data()

    def update_perfil(self, data: dict) -> bool:
        """Atualiza o perfil do usuário com os dados fornecidos."""
        return self.perfil_modal.update_perfil_data(data)
