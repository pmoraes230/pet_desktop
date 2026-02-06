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
            INNER JOIN consulta c ON p.ID = c.ID
            WHERE c.ID = %s
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
        """Retorna os últimos 5 alertas/notificações para o veterinário, com o nome do pet"""
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT p.NOME AS nome_pet, n.mensagem, n.data_criacao
            FROM pet_app_notificacao n
            INNER JOIN pet p ON n.ID = p.ID
            WHERE n.ID = %s
            ORDER BY n.data_criacao DESC
            LIMIT 5
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

