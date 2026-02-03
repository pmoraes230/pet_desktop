from ..models.vet_modal import VetModal

class VetController:
    def __init__(self, vet_id: int):
        self.vet_id = vet_id
        self.vet_modal = VetModal(vet_id)
        self.vet_data = None
        
    def fetch_vet_data(self) -> dict:
        """
        Recupera os dados do veterinário.
        
        Returns:
            dict: Dados do veterinário
        """
        try:
            self.vet_data = self.vet_modal.get_vet_data()
            return self.vet_data
        except Exception as e:
            print(f"Erro ao buscar dados do veterinário: {str(e)}")
            return {}