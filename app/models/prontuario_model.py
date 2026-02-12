from ..config.database import connectdb, closedb

class ProntuarioModel:
    def get_pets_do_vet(self, vet_id):
        """Retorna os pets para o prontuário"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            # Retorna todos os pets (não há relação direta entre pet e veterinário na estrutura)
            cursor.execute("""
                SELECT id, NOME
                FROM pet
                ORDER BY NOME
            """)
            resultado = cursor.fetchall()
            closedb(conn)
            return resultado
        except Exception as e:
            print(f"Erro ao buscar pets: {e}")
            return []

    def obter_historico(self, pet_id):
        """Retorna o histórico de prontuários do pet"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATA_CONSULTA, OBSERVACOES
                FROM consulta
                WHERE ID_PET = %s
                ORDER BY DATA_CONSULTA DESC
            """, (pet_id,))
            resultado = cursor.fetchall()
            closedb(conn)
            return resultado
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []

    def salvar_prontuario(self, pet_id, texto):
        """Salva um novo prontuário"""
        try:
            from uuid import uuid4
            conn = connectdb()
            cursor = conn.cursor()
            # Usa apenas hex do UUID (32 caracteres, sem hífens)
            consulta_id = uuid4().hex
            cursor.execute("""
                INSERT INTO consulta (id, ID_PET, OBSERVACOES, DATA_CONSULTA)
                VALUES (%s, %s, %s, NOW())
            """, (consulta_id, pet_id, texto))
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            print(f"Erro ao salvar prontuário: {e}")
            return False