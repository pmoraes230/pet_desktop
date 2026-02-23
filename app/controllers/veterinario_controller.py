from ..models.vet_modal import VetModal

class vetController:
    def __init__(self, vet_id: int):
        self.vet_id = vet_id

    def fetch_perfil_data(self) -> dict:
        """Busca os dados do veterinário usando o VetModal."""
        vet_data = VetModal(self.vet_id)
        return vet_data.get_vet_info()
    
    def update_perfil_data(self, nome: str, email: str, crmv: str, uf_crmv: str) -> dict:
        """Atualiza os dados do veterinário e retorna resultado para a view"""
        
        response = {
            "success": False,
            "message": "",
            "data": None,
            "errors": {}
        }

        # 1. Validações básicas (você pode aumentar conforme necessidade)
        if not nome or len(nome.strip()) < 3:
            response["errors"]["nome"] = "Nome deve ter pelo menos 3 caracteres"
        
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            response["errors"]["email"] = "E-mail parece inválido"
        
        if not crmv or not crmv.isdigit():
            response["errors"]["crmv"] = "CRMV deve conter apenas números"
        
        if not uf_crmv or len(uf_crmv) != 2 or not uf_crmv.isalpha():
            response["errors"]["uf_crmv"] = "UF do CRMV deve ter exatamente 2 letras"

        # Se tiver algum erro de validação → já retorna
        if response["errors"]:
            response["message"] = "Dados inválidos. Verifique os campos."
            return response

        # 2. Tenta atualizar no banco (chama a model)
        try:
            atualizado = self.update_vet_info(nome, email, crmv, uf_crmv)
            
            if atualizado:
                response["success"] = True
                response["message"] = "Dados atualizados com sucesso!"
            else:
                response["message"] = "Não foi possível atualizar os dados. Tente novamente."
                
        except Exception as e:
            print(f"Erro no controller update_perfil_data: {str(e)}")
            response["message"] = "Erro interno ao atualizar perfil. Contate o suporte."

        return response
