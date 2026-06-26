from ..config.database import connectdb, closedb
from datetime import datetime, date, timedelta
import calendar
import uuid


class AgendaController:
    def __init__(self, id_veterinario=None, vet_id=None):
        self.id_veterinario = id_veterinario if id_veterinario is not None else vet_id
        self.vet_id = self.id_veterinario

    def _como_data(self, valor):
        if not valor:
            return None
        if hasattr(valor, "date"):
            return valor.date()
        return valor

    def _status_normalizado(self, status):
        return (status or "").lower().replace("í", "i").replace("Ã­", "i")

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

    def buscar_consultas_do_dia(self, numero_dia, mes, ano):
        """Busca consultas do veterinario para um dia especifico."""
        data_consulta = f"{ano}-{mes:02d}-{numero_dia:02d}"

        if self.id_veterinario:
            return self._executar_com_coluna_vet("""
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA, c.STATUS,
                       p.NOME AS NOME_PET
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                WHERE DATE(c.DATA_CONSULTA) = %s
                  AND c.{vet_column} = %s
                ORDER BY c.HORARIO_CONSULTA ASC
            """, (data_consulta, self.id_veterinario))

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

    def buscar_consultas_da_semana(self, data_inicial_semana):
        """Busca consultas do veterinario entre domingo e sabado."""
        if not data_inicial_semana:
            return []

        data_inicio = data_inicial_semana.date()
        data_fim = (data_inicial_semana + timedelta(days=6)).date()

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
        if self.id_veterinario:
            params.append(self.id_veterinario)
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

    def buscar_consultas_do_mes(self, mes, ano):
        """Busca consultas do veterinario no mes."""
        if self.id_veterinario:
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
            """, (mes, ano, self.id_veterinario))

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

    def dias_com_consultas(self, mes, ano):
        consultas = self.buscar_consultas_do_mes(mes, ano)
        return {
            self._como_data(consulta["DATA_CONSULTA"]).day
            for consulta in consultas
            if consulta.get("DATA_CONSULTA")
        }

    def datas_com_consultas_do_mes(self, mes, ano):
        """Retorna as datas do mes que possuem consulta."""
        consultas = self.buscar_consultas_do_mes(mes, ano)
        return {
            self._como_data(consulta.get("DATA_CONSULTA"))
            for consulta in consultas
            if consulta.get("DATA_CONSULTA")
        }

    def resumo_calendario_mes(self, mes, ano):
        """Monta o backend do calendario completo, com semanas domingo-sabado."""
        consultas = self.buscar_consultas_do_mes(mes, ano)
        contagem_por_data = {}

        for consulta in consultas:
            data_consulta = self._como_data(consulta.get("DATA_CONSULTA"))
            if not data_consulta:
                continue
            contagem_por_data[data_consulta] = contagem_por_data.get(data_consulta, 0) + 1

        semanas = []
        for semana in calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes):
            semanas.append([
                {
                    "data": dia,
                    "dia": dia.day,
                    "fora_do_mes": dia.month != mes,
                    "tem_consulta": dia in contagem_por_data,
                    "total_consultas": contagem_por_data.get(dia, 0),
                }
                for dia in semana
            ])

        return {
            "mes": mes,
            "ano": ano,
            "semanas": semanas,
            "datas_com_consulta": set(contagem_por_data.keys()),
            "total_consultas": sum(contagem_por_data.values()),
        }

    def dias_com_consultas_na_semana(self, data_inicial_semana):
        try:
            if not data_inicial_semana:
                return set()

            consultas = self.buscar_consultas_da_semana(data_inicial_semana)
            inicio = data_inicial_semana.date()
            fim = (data_inicial_semana + timedelta(days=7)).date()

            dias_semana = set()
            for consulta in consultas:
                data_consulta = self._como_data(consulta.get("DATA_CONSULTA"))
                if data_consulta and inicio <= data_consulta < fim:
                    dias_semana.add(data_consulta)

            return dias_semana
        except Exception as e:
            print(f"Erro ao buscar dias com consultas na semana: {e}")
            return set()

    def liberar_horarios(self, data_str, hora_inicio_str, hora_fim_str, duracao_slot):
        """Cria vagas livres na agenda do veterinario."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado.", 0, 0

        try:
            duracao_slot = int(duracao_slot)
            if duracao_slot not in (15, 30, 45, 60):
                return False, "Intervalo invalido.", 0, 0

            data_vaga = datetime.strptime(data_str, "%d/%m/%Y").date()
            inicio = datetime.strptime(f"{data_str} {hora_inicio_str}", "%d/%m/%Y %H:%M")
            fim = datetime.strptime(f"{data_str} {hora_fim_str}", "%d/%m/%Y %H:%M")

            if data_vaga < date.today():
                return False, "Nao e possivel liberar horarios em uma data passada.", 0, 0

            if fim <= inicio:
                return False, "A hora de termino deve ser maior que a hora de inicio.", 0, 0

            criados = 0
            existentes = 0
            atual = inicio

            conn = connectdb()
            cursor = conn.cursor()

            while atual < fim:
                cursor.execute("""
                    SELECT id
                    FROM agenda_disponivel
                    WHERE ID_VETERINARIO = %s
                      AND DATA = %s
                      AND HORA = %s
                    LIMIT 1
                """, (self.id_veterinario, data_vaga, atual.time()))

                if cursor.fetchone():
                    existentes += 1
                else:
                    cursor.execute("""
                        INSERT INTO agenda_disponivel
                        (id, ID_VETERINARIO, DATA, HORA, STATUS)
                        VALUES (%s, %s, %s, %s, 'Livre')
                    """, (uuid.uuid4().hex, self.id_veterinario, data_vaga, atual.time()))
                    criados += 1

                atual += timedelta(minutes=duracao_slot)

            conn.commit()
            closedb(conn)
            return True, "Horarios liberados com sucesso.", criados, existentes
        except Exception as e:
            if 'conn' in locals():
                closedb(conn)
            return False, f"Erro ao liberar horarios: {e}", 0, 0

    def atualizar_status_consulta(self, consulta_id, novo_status):
        """Atualiza o status da consulta e sincroniza o slot quando necessario."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado."

        last_error = "Consulta nao encontrada."
        status_vaga = None
        novo_status_normalizado = self._status_normalizado(novo_status)
        if novo_status == "Confirmado":
            status_vaga = "Ocupado"
        elif novo_status == "Cancelado":
            status_vaga = "Livre"

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
                """, (consulta_id, self.id_veterinario))
                consulta = cursor.fetchone()

                if not consulta:
                    closedb(conn)
                    continue

                status_atual = self._status_normalizado(consulta.get("STATUS"))
                if novo_status_normalizado in ("confirmado", "cancelado") and status_atual != "pendente":
                    closedb(conn)
                    return False, f"Status atual: {consulta.get('STATUS')}. Nao e possivel alterar."

                if novo_status_normalizado == "concluido" and status_atual != "confirmado":
                    closedb(conn)
                    return False, f"Status atual: {consulta.get('STATUS')}. Nao e possivel finalizar."

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
                        self.id_veterinario,
                        consulta["DATA_CONSULTA"],
                        consulta["HORARIO_CONSULTA"],
                    ))

                conn.commit()
                closedb(conn)
                return True, "Consulta atualizada com sucesso."
            except Exception as e:
                if conn:
                    closedb(conn)
                last_error = e

        return False, f"Erro ao atualizar consulta: {last_error}"

    def excluir_consulta(self, consulta_id):
        """Remove uma consulta do veterinario e libera a vaga correspondente."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado."

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
                """, (consulta_id, self.id_veterinario))
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
                        self.id_veterinario,
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
