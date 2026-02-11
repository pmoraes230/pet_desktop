from ..models.tutores import listar_tutores_para_veterinario

class TutorController:
    def __init__(self, veterinario_id: str = None):
        self.veterinario_id = veterinario_id

    def listar_contatos(self) -> list[dict]:
        tutores_db = listar_tutores_para_veterinario(self.veterinario_id)
        return [
            {
                "id": t["id"],
                "nome": t["nome_tutor"],
                "avatar": t["avatar"]
            }
            for t in tutores_db
        ]