from ..models.pets_vet import PetAll

class PetController:
    def __init__(self):
        self.pet_model = PetAll()

    def listar_pets(self) -> list:
        """
        Retorna todos os pets cadastrados
        """
        try:
            return PetAll.listar_pets()   # ← chama na classe, não na instância
        except Exception as e:
            print(f"Erro ao listar pets: {str(e)}")
            return []

    def criar_pet(self, nome_pet, raca, idade, especie, id_tutor) -> bool:
        """
        Cria um novo pet
        """
        try:
            self.pet_model.criar_pet(
                nome_pet=nome_pet,
                raca=raca,
                idade=idade,
                especie=especie,
                id_tutor=id_tutor
            )
            return True
        except Exception as e:
            print(f"Erro ao criar pet: {str(e)}")
            return False

    def buscar_pet(self, id_pet: int) -> dict:
        """
        Busca um pet específico pelo ID
        """
        try:
            return self.pet_model.buscar_pet(id_pet)
        except Exception as e:
            print(f"Erro ao buscar pet: {str(e)}")
            return {}
