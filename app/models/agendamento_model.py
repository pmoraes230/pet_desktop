from ..config.database import connectdb, closedb
import uuid


class AgendamentoModel:
    def listar_pets_aceitos(self, vet_id):
        last_error = "Nenhum pet encontrado para este veterinario."
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(f"""
                    SELECT DISTINCT p.id, p.NOME AS nome
                    FROM pet p
                    INNER JOIN consulta c ON p.id = c.ID_PET
                    WHERE c.{vet_column} = %s
                      AND LOWER(COALESCE(c.STATUS, '')) IN ('confirmado', 'concluido', 'concluÃ­do')
                    ORDER BY p.NOME
                    LIMIT 100
                """, (vet_id,))
                pets = cursor.fetchall()
                closedb(conn)
                return pets
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        print(f"Erro ao listar pets aceitos: {last_error}")
        return []

    def listar_veterinarios(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, NOME AS nome FROM veterinario ORDER BY NOME LIMIT 100")
            vets = cursor.fetchall()
            closedb(conn)
            return vets
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao listar veterinarios: {e}")
            return []

    def criar_agendamento(self, id_consulta, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes, retorno_agendado):
        last_error = "Nao foi possivel criar agendamento."
        for vet_column in ("ID_VETERINARIO", "veterinario_id"):
            conn = None
            try:
                conn = connectdb()
                cursor = conn.cursor()

                cursor.execute(f"""
                    SELECT id
                    FROM consulta
                    WHERE {vet_column} = %s
                      AND DATA_CONSULTA = %s
                      AND HORARIO_CONSULTA = %s
                      AND COALESCE(STATUS, '') IN ('Pendente', 'Agendado', 'Confirmado')
                    LIMIT 1
                """, (id_veterinario, data, horario))
                if cursor.fetchone():
                    closedb(conn)
                    print("Erro ao criar agendamento: horario ja ocupado")
                    return False

                cursor.execute("""
                    SELECT id, STATUS
                    FROM agenda_disponivel
                    WHERE ID_VETERINARIO = %s
                      AND DATA = %s
                      AND HORA = %s
                    LIMIT 1
                """, (id_veterinario, data, horario))
                vaga = cursor.fetchone()

                if vaga and len(vaga) > 1 and vaga[1] == "Bloqueado":
                    closedb(conn)
                    print("Erro ao criar agendamento: horario bloqueado")
                    return False

                if vaga:
                    cursor.execute("""
                        UPDATE agenda_disponivel
                        SET STATUS = 'Ocupado'
                        WHERE ID_VETERINARIO = %s
                          AND DATA = %s
                          AND HORA = %s
                    """, (id_veterinario, data, horario))
                else:
                    cursor.execute("""
                        INSERT INTO agenda_disponivel
                        (id, ID_VETERINARIO, DATA, HORA, STATUS)
                        VALUES (%s, %s, %s, %s, 'Ocupado')
                    """, (uuid.uuid4().hex, id_veterinario, data, horario))

                cursor.execute(f"""
                    INSERT INTO consulta
                    (id, ID_PET, {vet_column}, DATA_CONSULTA, HORARIO_CONSULTA,
                     TIPO_DE_CONSULTA, OBSERVACOES, RETORNO_AGENDADO, STATUS)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Confirmado')
                """, (id_consulta, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes, retorno_agendado))
                conn.commit()
                closedb(conn)
                print(f"Agendamento criado com sucesso! ID: {id_consulta}")
                return True
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        print(f"Erro ao criar agendamento: {last_error}")
        return False

    def liberar_horarios(self, id_veterinario, data, horarios):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            criados = 0

            for hora in horarios:
                cursor.execute("""
                    SELECT id
                    FROM agenda_disponivel
                    WHERE ID_VETERINARIO = %s
                      AND DATA = %s
                      AND HORA = %s
                    LIMIT 1
                """, (id_veterinario, data, hora))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO agenda_disponivel
                            (id, ID_VETERINARIO, DATA, HORA, STATUS)
                        VALUES
                            (%s, %s, %s, %s, 'Livre')
                    """, (uuid.uuid4().hex, id_veterinario, data, hora))
                    criados += 1

            conn.commit()
            closedb(conn)
            return criados
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao liberar horarios: {e}")
            return 0
