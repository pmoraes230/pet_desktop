from ..config.database import connectdb, closedb
from datetime import datetime, timedelta
import uuid

class AgendamentoController:
    def __init__(self, vet_id=None):
        self.vet_id = vet_id

    def listar_pets(self):
        """Lista pets aceitos pelo veterinÃ¡rio logado."""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            if self.vet_id:
                query = """
                    SELECT DISTINCT p.id, p.NOME AS nome
                    FROM pet p
                    INNER JOIN consulta c ON c.ID_PET = p.id
                    WHERE c.veterinario_id = %s
                      AND c.STATUS IN ('Confirmado', 'Concluido')
                    ORDER BY p.NOME
                    LIMIT 100
                """
                cursor.execute(query, (self.vet_id,))
            else:
                query = "SELECT id, NOME AS nome FROM pet ORDER BY NOME LIMIT 100"
                cursor.execute(query)

            pets = cursor.fetchall()
            closedb(conn)
            return pets
        except Exception as e:
            print(f"Erro ao listar pets: {e}")
            return []

    def listar_veterinarios(self):
        """Lista todos os veterinários"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, NOME AS nome FROM veterinario ORDER BY NOME LIMIT 100"
            cursor.execute(query)
            vets = cursor.fetchall()
            closedb(conn)
            return vets
        except Exception as e:
            print(f"Erro ao listar veterinários: {e}")
            return []

    def criar_agendamento(self, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes):
        """Cria um novo agendamento no banco"""
        try:
            if not id_veterinario:
                print("Erro ao criar agendamento: veterinario logado nao informado")
                return False

            conn = connectdb()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM consulta
                WHERE veterinario_id = %s
                  AND DATA_CONSULTA = %s
                  AND HORARIO_CONSULTA = %s
                  AND STATUS IN ('Pendente', 'Confirmado')
            """, (id_veterinario, data, horario))
            if cursor.fetchone()[0] > 0:
                print("Erro ao criar agendamento: horario ja ocupado")
                closedb(conn)
                return False
            
            # Gera UUID sem hífens (32 caracteres) para caber no campo char(32)
            id_consulta = str(uuid.uuid4()).replace("-", "")
            
            query = """
                INSERT INTO consulta 
                (id, ID_PET, veterinario_id, DATA_CONSULTA, HORARIO_CONSULTA, TIPO_DE_CONSULTA, OBSERVACOES, STATUS)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')
            """
            
            cursor.execute(query, (id_consulta, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes))

            cursor.execute("""
                UPDATE agenda_disponivel
                SET STATUS = 'Ocupado'
                WHERE ID_VETERINARIO = %s
                  AND DATA = %s
                  AND HORA = %s
            """, (id_veterinario, data, horario))

            conn.commit()
            closedb(conn)
            print(f"Agendamento criado com sucesso! ID: {id_consulta}")
            return True
        except Exception as e:
            print(f"Erro ao criar agendamento: {e}")
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
                    SELECT ID
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
                            (ID, ID_VETERINARIO, DATA, HORA, STATUS)
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
