from ..config.database import connectdb
from django.contrib.auth.hashers import check_password, make_password

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
                SELECT v.id, 
                v.nome, 
                v.email, 
                v.CRMV, 
                e.sigla AS UF_CRMV,
                v.TELEFONE,
                v.imagem_perfil_veterinario
                FROM veterinario v
                JOIN pet_app_estado e ON v.UF_CRMV = e.id
                WHERE v.id = %s
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

    def update_vet_info(self, nome: str, email: str, crmv: str, uf_crmv: str) -> bool:
        """Atualizar as infomações do veterinário"""
        try:
            conn = connectdb()
            cursor = conn.cursor()
            query = """
                UPDATE veterinario SET
                NOME = %s, EMAIL = %s, CRMV = %s, UF_CRMV = %s
                WHERE id = %s
            """
            cursor.execute(query, (nome, email, crmv, uf_crmv, self.vet_id))
            cursor
            
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False

    def alterar_senha(self, senha_atual: str, nova_senha: str):
        conn = None
        cursor = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT senha_veterinario FROM veterinario WHERE id = %s",
                (self.vet_id,),
            )
            row = cursor.fetchone()
            if not row:
                return False, "Usuario nao encontrado"

            stored_hash = row[0]
            if not check_password(senha_atual, stored_hash):
                return False, "Senha atual incorreta"

            cursor.execute(
                "UPDATE veterinario SET senha_veterinario = %s WHERE id = %s",
                (make_password(nova_senha), self.vet_id),
            )
            conn.commit()
            return True, "Senha atualizada com sucesso"
        except Exception as e:
            print(f"Erro ao alterar senha: {e}")
            return False, "Erro ao atualizar senha"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
