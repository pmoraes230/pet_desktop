from ..config.database import connectdb
from datetime import datetime

class ProntuarioModel:
    def get_pets_do_vet(self, vet_id):
        conn = connectdb()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome
            FROM pets
            WHERE vet_id = %s
            ORDER BY nome
        """, (vet_id,))

        pets = cursor.fetchall()
        conn.close()

        return pets

    def salvar_prontuario(self, pet_id, vet_id, texto):
        conn = connectdb()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prontuarios (pet_id, vet_id, texto, data)
            VALUES (%s, %s, %s, %s)
        """, (pet_id, vet_id, texto, datetime.now()))

        conn.commit()
        conn.close()

    def get_historico(self, pet_id):
        conn = connectdb()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data, texto
            FROM prontuarios
            WHERE pet_id = %s
            ORDER BY data DESC
        """, (pet_id,))

        historico = cursor.fetchall()
        conn.close()

        return historico
