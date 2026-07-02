from ..config.database import connectdb, closedb
import uuid


class AgendaModel:
    def _executar_com_coluna_vet(self, query_template, params):
        last_error = None
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query_template.format(vet_column=vet_column), params)
                resultado = cursor.fetchall()
                closedb(conn)
                return resultado
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        print(f"Erro ao buscar consultas: {last_error}")
        return []

    def buscar_consultas_do_dia(self, data_consulta, id_veterinario=None):
        if id_veterinario:
            return self._executar_com_coluna_vet("""
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                       p.NOME AS NOME_PET
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                WHERE DATE(c.DATA_CONSULTA) = %s
                  AND c.{vet_column} = %s
                ORDER BY c.HORARIO_CONSULTA ASC
            """, (data_consulta, id_veterinario))

        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                       p.NOME AS NOME_PET
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                WHERE DATE(c.DATA_CONSULTA) = %s
                ORDER BY c.HORARIO_CONSULTA ASC
            """, (data_consulta,))
            consultas = cursor.fetchall()
            closedb(conn)
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas: {e}")
            return []

    def buscar_consultas_da_semana(self, data_inicio, data_fim, id_veterinario=None):
        query = """
            SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                   c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                   p.NOME AS NOME_PET,
                   t.NOME_TUTOR AS NOME_TUTOR
            FROM consulta c
            LEFT JOIN pet p ON p.id = c.ID_PET
            LEFT JOIN tutor t ON t.id = p.ID_TUTOR
            WHERE DATE(c.DATA_CONSULTA) BETWEEN %s AND %s
              {vet_filter}
            ORDER BY c.DATA_CONSULTA ASC, c.HORARIO_CONSULTA ASC
        """

        params = [data_inicio, data_fim]
        if id_veterinario:
            params.append(id_veterinario)
            return self._executar_com_coluna_vet(
                query.replace("{vet_filter}", "AND c.{vet_column} = %s"),
                tuple(params),
            )

        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query.replace("{vet_filter}", ""), tuple(params))
            consultas = cursor.fetchall()
            closedb(conn)
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas da semana: {e}")
            return []

    def buscar_consultas_do_mes(self, mes, ano, id_veterinario=None):
        if id_veterinario:
            return self._executar_com_coluna_vet("""
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                       p.NOME AS NOME_PET,
                       t.NOME_TUTOR AS NOME_TUTOR
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                LEFT JOIN tutor t ON t.id = p.ID_TUTOR
                WHERE MONTH(c.DATA_CONSULTA) = %s
                  AND YEAR(c.DATA_CONSULTA) = %s
                  AND c.{vet_column} = %s
                ORDER BY c.DATA_CONSULTA ASC
            """, (mes, ano, id_veterinario))

        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                       p.NOME AS NOME_PET,
                       t.NOME_TUTOR AS NOME_TUTOR
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                LEFT JOIN tutor t ON t.id = p.ID_TUTOR
                WHERE MONTH(c.DATA_CONSULTA) = %s
                  AND YEAR(c.DATA_CONSULTA) = %s
                ORDER BY c.DATA_CONSULTA ASC
            """, (mes, ano))
            consultas = cursor.fetchall()
            closedb(conn)
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas do mes: {e}")
            return []

    def liberar_horario(self, cursor, id_veterinario, data_vaga, hora):
        cursor.execute("""
            SELECT id
            FROM agenda_disponivel
            WHERE ID_VETERINARIO = %s
              AND DATA = %s
              AND HORA = %s
            LIMIT 1
        """, (id_veterinario, data_vaga, hora))

        if cursor.fetchone():
            return False

        cursor.execute("""
            INSERT INTO agenda_disponivel
            (id, ID_VETERINARIO, DATA, HORA, STATUS)
            VALUES (%s, %s, %s, %s, 'Livre')
        """, (uuid.uuid4().hex, id_veterinario, data_vaga, hora))
        return True

    def salvar_horarios_liberados(self, id_veterinario, data_vaga, horarios):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            criados = 0
            existentes = 0

            for hora in horarios:
                if self.liberar_horario(cursor, id_veterinario, data_vaga, hora):
                    criados += 1
                else:
                    existentes += 1

            conn.commit()
            closedb(conn)
            return True, "Horarios liberados com sucesso.", criados, existentes
        except Exception as e:
            if conn:
                closedb(conn)
            return False, f"Erro ao liberar horarios: {e}", 0, 0

    def atualizar_status_consulta(self, consulta_id, id_veterinario, novo_status, status_vaga=None):
        last_error = "Consulta nao encontrada."
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(f"""
                    SELECT id, DATA_CONSULTA, HORARIO_CONSULTA, STATUS
                    FROM consulta
                    WHERE id = %s AND {vet_column} = %s
                    LIMIT 1
                """, (consulta_id, id_veterinario))
                consulta = cursor.fetchone()

                if not consulta:
                    closedb(conn)
                    continue

                cursor.execute("""
                    UPDATE consulta
                    SET STATUS = %s
                    WHERE id = %s
                """, (novo_status, consulta_id))

                if status_vaga and consulta.get("DATA_CONSULTA") and consulta.get("HORARIO_CONSULTA"):
                    cursor.execute("""
                        UPDATE agenda_disponivel
                        SET STATUS = %s
                        WHERE ID_VETERINARIO = %s
                          AND DATA = %s
                          AND HORA = %s
                    """, (
                        status_vaga,
                        id_veterinario,
                        consulta["DATA_CONSULTA"],
                        consulta["HORARIO_CONSULTA"],
                    ))

                conn.commit()
                closedb(conn)
                return True, "Consulta atualizada com sucesso.", consulta
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        return False, f"Erro ao atualizar consulta: {last_error}", None

    def buscar_consulta_do_vet(self, consulta_id, id_veterinario):
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(f"""
                    SELECT id, DATA_CONSULTA, HORARIO_CONSULTA, STATUS
                    FROM consulta
                    WHERE id = %s AND {vet_column} = %s
                    LIMIT 1
                """, (consulta_id, id_veterinario))
                consulta = cursor.fetchone()
                closedb(conn)
                if consulta:
                    return consulta
            except Exception:
                if conn:
                    closedb(conn)
        return None

    def excluir_consulta(self, consulta_id, id_veterinario):
        last_error = "Consulta nao encontrada."
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(f"""
                    SELECT id, DATA_CONSULTA, HORARIO_CONSULTA
                    FROM consulta
                    WHERE id = %s AND {vet_column} = %s
                    LIMIT 1
                """, (consulta_id, id_veterinario))
                consulta = cursor.fetchone()

                if not consulta:
                    closedb(conn)
                    continue

                if consulta.get("DATA_CONSULTA") and consulta.get("HORARIO_CONSULTA"):
                    cursor.execute("""
                        UPDATE agenda_disponivel
                        SET STATUS = 'Livre'
                        WHERE ID_VETERINARIO = %s
                          AND DATA = %s
                          AND HORA = %s
                    """, (
                        id_veterinario,
                        consulta["DATA_CONSULTA"],
                        consulta["HORARIO_CONSULTA"],
                    ))

                cursor.execute("DELETE FROM consulta WHERE id = %s", (consulta_id,))
                conn.commit()
                closedb(conn)
                return True, "Consulta removida com sucesso."
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        return False, f"Erro ao excluir consulta: {last_error}"
