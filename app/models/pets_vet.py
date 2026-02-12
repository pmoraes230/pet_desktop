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
            SELECT id, NOME, ESPECIE, RACA, DATA_NASCIMENTO, SEXO, PESO, CASTRADO, PERSONALIDADE, IMAGEM, ID_TUTOR
            FROM pet
            WHERE id = %s
        """, (id_pet,))

        pet = cursor.fetchone()
        conn.close()
        return pet

    @staticmethod
    def atualizar_imagem_pet(id_pet, imagem_key):
        """Atualiza a imagem do pet no banco de dados"""
        try:
            conn = connectdb()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pet 
                SET IMAGEM = %s 
                WHERE id = %s
            """, (imagem_key, id_pet))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar imagem do pet: {e}")
            return False
