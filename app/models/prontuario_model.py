from ..config.database import connectdb, closedb

class ProntuarioModel:
    def get_pets_do_vet(self, vet_id):
        """Retorna os pets do veterinário"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome
                FROM pet
                WHERE id_veterinario = %s
                ORDER BY nome
            """, (vet_id,))
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
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consulta (ID_PET, OBSERVACOES, DATA_CONSULTA)
                VALUES (%s, %s, NOW())
            """, (pet_id, texto))
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            print(f"Erro ao salvar prontuário: {e}")
            return False