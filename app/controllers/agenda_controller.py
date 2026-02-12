from ..config.database import connectdb, closedb
from datetime import datetime
import calendar

class AgendaController:
    def __init__(self):
        pass

    def buscar_consultas_do_dia(self, numero_dia, mes, ano):
        """Busca consultas do banco para um dia específico"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            data_consulta = f"{ano}-{mes:02d}-{numero_dia:02d}"
            
            query = """
                SELECT c.id, c.HORARIO_CONSULTA, c.TIPO_DE_CONSULTA, 
                       c.ID_VETERINARIO, c.ID_PET, c.OBSERVACOES, c.DATA_CONSULTA
                FROM consulta c
                WHERE DATE(c.DATA_CONSULTA) = %s
                ORDER BY c.HORARIO_CONSULTA ASC
            """
            
            cursor.execute(query, (data_consulta,))
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
                       c.ID_VETERINARIO, c.ID_PET, c.DATA_CONSULTA
                FROM consulta c
                WHERE MONTH(c.DATA_CONSULTA) = %s AND YEAR(c.DATA_CONSULTA) = %s
                ORDER BY c.DATA_CONSULTA ASC
            """
            
            cursor.execute(query, (mes, ano))
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