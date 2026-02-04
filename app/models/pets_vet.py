from ..config.database import connectdb

class PetAll:
    @staticmethod
    def listar_pets():
        conn = connectdb()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM pet
        """)

        pets = cursor.fetchall()
        conn.close()
        return pets


    @staticmethod
    def buscar_pet(id_pet):
        conn = connectdb()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                p.*, 
                t.nome AS nome_tutor, 
                t.telefone
            FROM pets p
            JOIN tutores t ON t.id_tutor = p.id_tutor
            WHERE p.id_pet = %s
        """, (id_pet,))

        pet = cursor.fetchone()
        conn.close()
        return pet
