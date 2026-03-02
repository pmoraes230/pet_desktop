from ..models.pets_vet import PetAll
import uuid
from datetime import datetime

class PetController:
    def __init__(self):
        self.pet_model = PetAll()

    def listar_pets(self) -> list:
        try:
            return self.pet_model.listar_pets()
        except Exception as e:
            print(f"Erro ao listar pets: {e}")
            return []

    def criar_pet(self, nome_pet, raca, idade, especie, id_tutor: str) -> bool:
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
            print(f"Erro ao criar pet: {e}")
            return False

    def buscar_pet(self, id_pet: str) -> dict:
        try:
            return self.pet_model.buscar_pet(id_pet)
        except Exception as e:
            print(f"Erro ao buscar pet: {e}")
            return {}

    def atualizar_imagem_pet(self, id_pet: str, imagem_key: str) -> bool:
        try:
            return self.pet_model.atualizar_imagem_pet(id_pet, imagem_key)
        except Exception as e:
            print(f"Erro ao atualizar imagem: {e}")
            return False

    def buscar_tutor_por_pet(self, id_pet: str) -> dict:
        try:
            return self.pet_model.buscar_tutor_por_pet_id(id_pet)
        except Exception as e:
            print(f"Erro ao buscar tutor: {e}")
            return {}

    def buscar_vacinas_por_pet(self, id_pet: str) -> list:
        try:
            return self.pet_model.buscar_vacinas_por_pet_id(id_pet)
        except Exception as e:
            print(f"Erro ao buscar vacinas: {e}")
            return []

    def adicionar_vacina(self, id_pet: str, nome_vacina: str, proxima_dose: str) -> bool:
        try:
            return self.pet_model.adicionar_vacina(id_pet, nome_vacina, proxima_dose)
        except Exception as e:
            print(f"Erro ao adicionar vacina: {e}")
            return False

    # ---------------- MEDICAMENTOS ----------------

    def buscar_medicamentos_por_pet(self, id_pet: str) -> list:
        try:
            return self.pet_model.buscar_medicamentos(id_pet)
        except Exception as e:
            print(f"Erro ao buscar medicamentos: {e}")
            return []

    

    def adicionar_medicamento(self, id_pet: str, nome: str, dosagem: str,
                        frequencia: str, inicio=None, termino=None) -> bool:
        try:
            # Aqui já vem no formato YYYY-MM-DD do módulo
            return self.pet_model.adicionar_medicamento(
                id_pet,
                nome,
                dosagem,
                frequencia,
                inicio,
                termino
            )
        except Exception as e:
            print(f"Erro no controller: {e}")
            return False

    # ---------------- EMOCIONAL ----------------

    def buscar_historico_emocional(self, id_pet: str) -> list:
        try:
            return self.pet_model.buscar_historico_emocional(id_pet)
        except Exception as e:
            print(f"Erro ao buscar histórico emocional: {e}")
            return []