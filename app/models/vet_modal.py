from ..config.database import connectdb

class VetModal:
    def __init__(self, vet_id: int):
        self.vet_id = vet_id
        self.vet_data = None
        
    def get_vet_data(self) -> dict:
        """
        Recupera os dados do veterinário do banco de dados.
        
        Returns:
            dict: Dados do veterinário
        """
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT id, nome, email, CRMV, UF_CRMV, TELEFONE, imagem_perfil_veterinario, pessoa_fisica_id OR pessoa_juridica_id
                FROM veterinario 
                WHERE id = %s
            """
            cursor.execute(query, (self.vet_id,))
            result = cursor.fetchone()
            
            if result:
                self.vet_data = result
                return self.vet_data
            else:
                return {}
                
        except Exception as e:
            print(f"Erro ao recuperar dados do veterinário: {str(e)}")
            return {}
        
        finally:
            if conn:
                conn.close()