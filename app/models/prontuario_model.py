from ..config.database import connectdb, closedb

class ProntuarioModel:
    def get_pets_do_vet(self, vet_id):
        """Retorna os pets para o prontuário"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            # Retorna apenas pets com consulta aceita para este veterinário.
            cursor.execute("""
                SELECT DISTINCT p.id, p.NOME
                FROM pet p
                INNER JOIN consulta c ON c.ID_PET = p.id
                WHERE c.veterinario_id = %s
                  AND c.STATUS IN ('Confirmado', 'Concluido')
                ORDER BY p.NOME
            """, (vet_id,))
            resultado = cursor.fetchall()
            closedb(conn)
            return resultado
        except Exception as e:
            print(f"Erro ao buscar pets: {e}")
            return []

    def obter_historico(self, pet_id, vet_id):
        """Retorna o histórico de prontuários do pet"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id,
                       HISTORICO_VETERINARIO,
                       MOTIVO_CONSULTA,
                       AVALIACAO_GERAL,
                       PROCEDIMENTOS,
                       DIAGNOSTICO_CONSLUSIVO,
                       OBSERVACAO,
                       DATA_CRIACAO,
                       arquivo
                FROM prontuariopet
                WHERE ID_PET = %s
                  AND ID_VETERINARIO = %s
                ORDER BY DATA_CRIACAO DESC
            """, (pet_id, vet_id))
            resultado = cursor.fetchall()
            closedb(conn)
            return resultado
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []

    def salvar_prontuario(self, pet_id, vet_id, texto, arquivo=None):
        """Salva um novo prontuário"""
        try:
            from uuid import uuid4
            conn = connectdb()
            cursor = conn.cursor()
            # Usa apenas hex do UUID (32 caracteres, sem hífens)
            consulta_id = uuid4().hex
            cursor.execute("""
                INSERT INTO prontuariopet
                    (id, ID_PET, ID_VETERINARIO, AVALIACAO_GERAL, OBSERVACAO, arquivo, DATA_CRIACAO)
                VALUES
                    (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                consulta_id,
                pet_id,
                vet_id,
                "Registrado pelo veterinario via desktop",
                texto,
                arquivo
            ))
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            print(f"Erro ao salvar prontuário: {e}")
            return False
