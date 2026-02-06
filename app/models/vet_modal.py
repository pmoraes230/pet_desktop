from ..config.database import connectdb

class VetModal:
    def __init__(self, vet_id: int):
        self.vet_id = vet_id
        self.vet_data = None

    def get_vet_info(self) -> dict:
        """Retorna os dados do veterinário."""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT id, nome, email, CRMV, UF_CRMV, TELEFONE, imagem_perfil_veterinario
                FROM veterinario 
                WHERE id = %s
            """
            cursor.execute(query, (self.vet_id,))
            result = cursor.fetchone()
            return result or {}
        except Exception as e:
            print(f"Erro ao recuperar dados do veterinário: {str(e)}")
            return {}
        finally:
            if conn:
                conn.close()

    def get_recent_pets(self) -> list:
        """Retorna os últimos pets atendidos pelo veterinário."""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.nome AS nome_pet, p.especie AS ESPECIE, p.raca AS RACA
                FROM pets p
                INNER JOIN consultas c ON p.id = c.pet_id
                WHERE c.vet_id = %s
                ORDER BY c.data DESC
                LIMIT 10
            """
            cursor.execute(query, (self.vet_id,))
            results = cursor.fetchall()
            return results or []
        except Exception as e:
            print(f"Erro ao buscar pets: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
