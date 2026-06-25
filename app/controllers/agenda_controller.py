from ..config.database import connectdb, closedb
from datetime import datetime, timedelta
import calendar

class AgendaController:
    def __init__(self, vet_id=None):
        self.vet_id = vet_id

    def buscar_consultas_do_dia(self, numero_dia, mes, ano):
        """Busca consultas do banco para um dia específico"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            data_consulta = f"{ano}-{mes:02d}-{numero_dia:02d}"
            
            query = """
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, p.NOME AS NOME_PET, c.OBSERVACOES,
                       c.DATA_CONSULTA, c.STATUS, c.veterinario_id
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                WHERE DATE(c.DATA_CONSULTA) = %s
                  AND (%s IS NULL OR c.veterinario_id = %s)
                ORDER BY c.HORARIO_CONSULTA ASC
            """

            cursor.execute(query, (data_consulta, self.vet_id, self.vet_id))
            consultas = cursor.fetchall()
            closedb(conn)
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas: {e}")
            return []

    def buscar_consultas_do_mes(self, mes, ano):
        """Busca todas as consultas do mês"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA,
                       c.ID_PET, p.NOME AS NOME_PET, c.DATA_CONSULTA,
                       c.STATUS, c.veterinario_id
                FROM consulta c
                LEFT JOIN pet p ON p.id = c.ID_PET
                WHERE MONTH(c.DATA_CONSULTA) = %s
                  AND YEAR(c.DATA_CONSULTA) = %s
                  AND (%s IS NULL OR c.veterinario_id = %s)
                ORDER BY c.DATA_CONSULTA ASC, c.HORARIO_CONSULTA ASC
            """

            cursor.execute(query, (mes, ano, self.vet_id, self.vet_id))
            consultas = cursor.fetchall()
            closedb(conn)
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas do mês: {e}")
            return []

    def dias_com_consultas(self, mes, ano):
        """Retorna lista de dias que têm consultas"""
        consultas = self.buscar_consultas_do_mes(mes, ano)
        dias = set()
        for consulta in consultas:
            data = consulta['DATA_CONSULTA']
            dias.add(data.day)
        return dias

    def dias_com_consultas_na_semana(self, data_inicial_semana):
        """Retorna um conjunto de datas (date) com consultas na semana informada."""
        try:
            if not data_inicial_semana:
                return set()

            mes = data_inicial_semana.month
            ano = data_inicial_semana.year
            consultas = self.buscar_consultas_do_mes(mes, ano)

            dias_semana = set()
            for consulta in consultas:
                data_consulta = consulta['DATA_CONSULTA']
                if hasattr(data_consulta, "date"):
                    data_consulta = data_consulta.date()

                inicio = data_inicial_semana.date()
                fim = (data_inicial_semana + timedelta(days=7)).date()
                if inicio <= data_consulta < fim:
                    dias_semana.add(data_consulta)

            return dias_semana
        except Exception as e:
            print(f"Erro ao buscar dias com consultas na semana: {e}")
            return set()
