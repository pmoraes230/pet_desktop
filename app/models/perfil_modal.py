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

    def update_perfil_data(self, data: dict) -> bool:
        """Atualiza os campos do perfil no banco de dados.

        Espera um dicionário `data` com chaves possíveis: NOME, EMAIL, CRMV, UF_CRMV, TELEFONE
        Retorna True se a atualização ocorreu com sucesso.
        """
        conn = None
        cursor = None
        try:
            conn = connectdb()
            cursor = conn.cursor()

            # Construir query dinâmica baseada nos campos fornecidos
            fields = []
            values = []
            allowed = {"NOME": "NOME", "EMAIL": "EMAIL", "CRMV": "CRMV", "UF_CRMV": "UF_CRMV", "TELEFONE": "TELEFONE"}
            for k, v in data.items():
                if k in allowed:
                    fields.append(f"{allowed[k]} = %s")
                    values.append(v)

            if not fields:
                return False

            values.append(self.perfil_id)
            query = f"UPDATE veterinario SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(query, tuple(values))
            conn.commit()
            return True

        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
