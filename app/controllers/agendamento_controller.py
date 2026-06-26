from ..config.database import connectdb, closedb
from datetime import datetime, date, timedelta
import uuid


class AgendamentoController:
    def __init__(self, vet_id=None):
        self.vet_id = vet_id

    def listar_pets(self, id_veterinario=None):
        """Lista apenas pets aceitos pelo veterinario logado."""
        vet_id = id_veterinario if id_veterinario is not None else self.vet_id
        if not vet_id:
            return []

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
                      AND LOWER(COALESCE(c.STATUS, '')) IN ('confirmado', 'concluido', 'concluído')
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
        """Lista todos os veterinarios."""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, NOME AS nome FROM veterinario ORDER BY NOME LIMIT 100"
            cursor.execute(query)
            vets = cursor.fetchall()
            closedb(conn)
            return vets
        except Exception as e:
            print(f"Erro ao listar veterinarios: {e}")
            return []

    def criar_agendamento(self, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes):
        """Cria um retorno confirmado para um pet ja aceito pelo veterinario."""
        if not id_veterinario:
            print("Erro ao criar agendamento: veterinario nao informado")
            return False

        try:
            data_consulta = datetime.strptime(data, "%Y-%m-%d").date() if isinstance(data, str) else data
            datetime.strptime(horario, "%H:%M") if isinstance(horario, str) else horario
        except Exception:
            print("Erro ao criar agendamento: data ou horario invalido")
            return False

        if data_consulta < date.today():
            print("Erro ao criar agendamento: nao e possivel marcar retorno em data passada")
            return False

        tipo_consulta = tipo_consulta or "Retorno"
        observacoes = (observacoes or "")[:255]
        retorno_agendado = data if tipo_consulta == "Retorno" else None
        id_consulta = uuid.uuid4().hex
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

    def liberar_horarios(self, id_veterinario, data, hora_inicio, hora_fim, intervalo_minutos=30):
        """Cria horarios livres na agenda_disponivel para o veterinario."""
        try:
            if not id_veterinario:
                print("Erro ao liberar horarios: veterinario logado nao informado")
                return 0

            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fim = datetime.strptime(hora_fim, "%H:%M")
            if inicio >= fim:
                print("Erro ao liberar horarios: hora inicial deve ser menor que hora final")
                return 0

            intervalo_minutos = int(intervalo_minutos)
            if intervalo_minutos <= 0:
                return 0

            conn = connectdb()
            cursor = conn.cursor()
            criados = 0
            atual = inicio

            while atual < fim:
                hora = atual.strftime("%H:%M")
                cursor.execute("""
                    SELECT id
                    FROM agenda_disponivel
                    WHERE ID_VETERINARIO = %s
                      AND DATA = %s
                      AND HORA = %s
                    LIMIT 1
                """, (id_veterinario, data, hora))
                existente = cursor.fetchone()

                if not existente:
                    cursor.execute("""
                        INSERT INTO agenda_disponivel
                            (id, ID_VETERINARIO, DATA, HORA, STATUS)
                        VALUES
                            (%s, %s, %s, %s, 'Livre')
                    """, (uuid.uuid4().hex, id_veterinario, data, hora))
                    criados += 1

                atual += timedelta(minutes=intervalo_minutos)

            conn.commit()
            closedb(conn)
            return criados
        except Exception as e:
            print(f"Erro ao liberar horarios: {e}")
            return 0
