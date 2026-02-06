from ..config.database import connectdb

class PerfilModal:
    def __init__(self, perfil_id: int):
        self.perfil_id = perfil_id
        self.perfil_data = None
        
    def get_perfil_data(self) -> dict:
        """Recupera os dados do perfil do banco de dados"""
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT ID, NOME, EMAIL, CRMV, UF_CRMV, TELEFONE, imagem_perfil_veterinario
                FROM veterinario 
                WHERE ID = %s
            """
            cursor.execute(query, (self.perfil_id,))
            result = cursor.fetchone()
            
            if result:
                self.perfil_data = result
                return self.perfil_data
            return {}
                
        except Exception as e:
            print(f"Erro ao recuperar dados do perfil: {str(e)}")
            return {}
        
        finally:
            if conn and conn.is_connected():
                conn.close()
