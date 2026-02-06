from ..config.database import connectdb

class PetAll:
    def listar_pets():
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, NOME, ESPECIE, RACA, DATA_NASCIMENTO, SEXO, PESO, CASTRADO, PERSONALIDADE, IMAGEM, ID_TUTOR
                FROM pet
                ORDER BY NOME
            """)

            pets = cursor.fetchall()

            conn.close()
            return pets

        except Exception as e:
            print(f"Erro ao listar pets: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return []


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
