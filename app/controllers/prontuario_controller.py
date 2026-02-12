from ..models.prontuario_model import ProntuarioModel

class ProntuarioController:
    def __init__(self, vet_id):
        self.vet_id = vet_id
        self.model = ProntuarioModel()

    def listar_pets(self):
        return self.model.get_pets_do_vet(self.vet_id)

    def salvar(self, pet_id, texto):
        self.model.salvar_prontuario(pet_id, self.vet_id, texto)

    def historico(self, pet_id):
        return self.model.get_historico(pet_id)
