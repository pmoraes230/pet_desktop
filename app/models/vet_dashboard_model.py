from ..config.database import connectdb, closedb


class VetDashboardModel:
    def __init__(self, vet_id):
        self.vet_id = vet_id

    def fetch_recent_pets(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.NOME AS nome_pet, p.ESPECIE AS especie, p.RACA AS raca
                FROM pet p
                INNER JOIN consulta c ON p.ID = c.ID_PET
                WHERE c.veterinario_id = %s
                  AND c.STATUS IN ('Confirmado', 'Concluido')
                ORDER BY c.DATA_CONSULTA DESC
                LIMIT 5
            """, (self.vet_id,))
            result = cursor.fetchall()
            closedb(conn)
            return result
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao buscar pets no dashboard: {str(e)}")
            return []

    def fetch_alerts(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT n.id, n.mensagem, n.tipo, n.data_criacao, n.lida, n.tutor_id, n.veterinario_id
                FROM pet_app_notificacao n
                WHERE n.veterinario_id = %s
                ORDER BY n.data_criacao DESC
                LIMIT 10
            """, (self.vet_id,))
            result = cursor.fetchall()
            closedb(conn)
            return result
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao buscar alertas: {str(e)}")
            return []

    def fetch_unread_count(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM pet_app_notificacao WHERE veterinario_id = %s AND lida = 0",
                (self.vet_id,)
            )
            count = cursor.fetchone()[0] or 0
            closedb(conn)
            return count
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao contar notificacoes nao lidas: {e}")
            return 0

    def mark_all_read(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pet_app_notificacao SET lida = 1 WHERE veterinario_id = %s AND lida = 0",
                (self.vet_id,)
            )
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao marcar notificacoes como lidas: {e}")
            return False

    def mark_notification_read(self, notification_id):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pet_app_notificacao SET lida = 1 WHERE id = %s",
                (notification_id,)
            )
            conn.commit()
            closedb(conn)
            return True
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao marcar notificacao {notification_id} como lida: {e}")
            return False

    def fetch_metrics(self):
        conn = None
        try:
            conn = connectdb()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(DISTINCT p.ID)
                FROM pet p
                INNER JOIN consulta c ON p.ID = c.ID_PET
                WHERE c.veterinario_id = %s
                  AND c.STATUS IN ('Confirmado', 'Concluido')
            """, (self.vet_id,))
            total_pets = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM consulta
                WHERE veterinario_id = %s AND DATE(DATA_CONSULTA) = CURDATE()
            """, (self.vet_id,))
            consultas_hoje = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM(VALOR_CONSULTA)
                FROM consulta
                WHERE veterinario_id = %s AND MONTH(DATA_CONSULTA) = MONTH(CURDATE())
            """, (self.vet_id,))
            faturamento_mes = cursor.fetchone()[0] or 0.0

            closedb(conn)
            return {
                "total_pets": total_pets,
                "consultas_hoje": consultas_hoje,
                "faturamento_mes": faturamento_mes,
            }
        except Exception as e:
            if conn:
                closedb(conn)
            print(f"Erro ao buscar metricas: {e}")
            return {
                "total_pets": 0,
                "consultas_hoje": 0,
                "faturamento_mes": 0.0,
            }
