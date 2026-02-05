from ..models.layout_Veterinario import dados_perfil_veterinario

class VeterinarioController:
    def __init__(self, perfil_id: int):
        self.perfil_id = perfil_id
        self.veterinario_data = None

    def perfil_veterinario(self) -> dict:
        """
        Recupera o perfil do veterinário e os pets atendidos.
        """
        try:
            dados = dados_perfil_veterinario(self.perfil_id)

            if not dados:
                return {
                    "success": False,
                    "message": "Veterinário não encontrado ou sem consultas"
                }

            self.veterinario_data = {
                "success": True,
                "veterinario_id": self.perfil_id,
                "pets_atendidos": dados
            }

            return self.veterinario_data

        except Exception as e:
            return {
                "success": False,
                "message": "Erro ao carregar perfil do veterinário",
                "error": str(e)
            }
