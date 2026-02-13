from ..config.database import connectdb

class VetController:
    def __init__(self, vet_id):
        self.vet_id = vet_id
        self.conn = connectdb()  # Conexão com o banco

    def fetch_recent_pets(self):
        """Retorna os últimos 5 pets atendidos pelo veterinário"""
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT p.NOME AS nome_pet, p.ESPECIE AS especie, p.RACA AS raca
            FROM pet p
            INNER JOIN consulta c ON p.ID = c.ID_PET
            WHERE c.ID_VETERINARIO = %s
            ORDER BY c.DATA_CONSULTA DESC
            LIMIT 5
        """
        try:
            cursor.execute(query, (self.vet_id,))
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Erro ao buscar pets no dashboard: {str(e)}")
            return []
        finally:
            cursor.close()



    def fetch_alerts(self):
        """Retorna as notificações do veterinário (tabela pet_app_notificacao)."""
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT n.id, n.mensagem, n.tipo, n.data_criacao, n.lida, n.tutor_id, n.veterinario_id
            FROM pet_app_notificacao n
            WHERE n.veterinario_id = %s
            ORDER BY n.data_criacao DESC
            LIMIT 10
        """
        try:
            cursor.execute(query, (self.vet_id,))
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Erro ao buscar alertas: {str(e)}")
            return []
        finally:
            cursor.close()

    def fetch_unread_count(self):
        """Retorna a quantidade de notificações não lidas do veterinário."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM pet_app_notificacao WHERE veterinario_id = %s AND lida = 0",
                (self.vet_id,)
            )
            count = cursor.fetchone()[0] or 0
            return count
        except Exception as e:
            print(f"Erro ao contar notificações não lidas: {e}")
            return 0
        finally:
            cursor.close()

    def mark_all_read(self):
        """Marca todas as notificações desse veterinário como lidas."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE pet_app_notificacao SET lida = 1 WHERE veterinario_id = %s AND lida = 0",
                (self.vet_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao marcar notificações como lidas: {e}")
            return False
        finally:
            cursor.close()

    def mark_notification_read(self, notification_id):
        """Marca uma notificação específica como lida."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE pet_app_notificacao SET lida = 1 WHERE id = %s",
                (notification_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao marcar notificação {notification_id} como lida: {e}")
            return False
        finally:
            cursor.close()

    def fetch_metrics(self):
        cursor = self.conn.cursor()

        # Total de pacientes
        cursor.execute("""
            SELECT COUNT(DISTINCT p.ID)
            FROM pet p
            INNER JOIN consulta c ON p.ID = c.ID_PET
            WHERE c.ID_VETERINARIO = %s
        """, (self.vet_id,))
        total_pets = cursor.fetchone()[0] or 0

        # Consultas hoje
        cursor.execute("""
            SELECT COUNT(*) 
            FROM consulta 
            WHERE ID_VETERINARIO = %s AND DATE(DATA_CONSULTA) = CURDATE()
        """, (self.vet_id,))
        consultas_hoje = cursor.fetchone()[0] or 0

        # Faturamento do mês
        cursor.execute("""
            SELECT SUM(VALOR_CONSULTA) 
            FROM consulta 
            WHERE ID_VETERINARIO = %s AND MONTH(DATA_CONSULTA) = MONTH(CURDATE())
        """, (self.vet_id,))
        faturamento_mes = cursor.fetchone()[0] or 0.0

        cursor.close()
        return {
            "total_pets": total_pets,
            "consultas_hoje": consultas_hoje,
            "faturamento_mes": faturamento_mes
        }

