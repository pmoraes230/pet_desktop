from ..config.database import connectdb, closedb


class ProntuarioModel:
    def get_pets_do_vet(self, vet_id):
        """Retorna apenas pets aceitos pelo veterinario."""
        last_error = None
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(f"""
                    SELECT DISTINCT p.id, p.NOME
                    FROM pet p
                    INNER JOIN consulta c ON p.id = c.ID_PET
                    WHERE c.{vet_column} = %s
                      AND LOWER(COALESCE(c.STATUS, '')) IN ('confirmado', 'concluido', 'concluido')
                    ORDER BY p.NOME
                """, (vet_id,))
                resultado = cursor.fetchall()
                closedb(conn)
                return resultado
            except Exception as e:
                last_error = e
                if conn:
                    closedb(conn)

        print(f"Erro ao buscar pets: {last_error}")
        return []

    def obter_historico(self, pet_id, vet_id):
        """Retorna o historico de prontuarios do pet."""
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
            print(f"Erro ao buscar historico: {e}")
            return []

    def salvar_prontuario(self, pet_id, vet_id, texto, arquivo=None):
        """Salva um novo prontuario."""
        try:
            from uuid import uuid4

            conn = connectdb()
            cursor = conn.cursor()
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
                arquivo,
            ))
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            print(f"Erro ao salvar prontuario: {e}")
            return False
