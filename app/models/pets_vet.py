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
    @staticmethod
    def buscar_tutor_por_pet_id(id_pet):
        """Busca os dados do tutor de um pet"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            # Primeiro, busca o ID_TUTOR do pet
            cursor.execute("""
                SELECT ID_TUTOR FROM pet WHERE id = %s
            """, (id_pet,))
            
            pet_result = cursor.fetchone()
            
            if not pet_result:
                conn.close()
                return {}
            
            id_tutor = pet_result.get('ID_TUTOR')
            
            if not id_tutor:
                conn.close()
                return {}
            
            # Busca os dados do tutor na tabela tutor
            cursor.execute("""
                SELECT * FROM tutor WHERE id = %s
            """, (id_tutor,))
            
            tutor = cursor.fetchone()
            conn.close()
            
            if tutor:
                return tutor
            else:
                return {}
                
        except Exception as e:
            print(f"Erro ao buscar tutor do pet: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals():
                conn.close()
            return {}

    @staticmethod
    def buscar_vacinas_por_pet_id(id_pet):
        """Busca as vacinas de um pet"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            
            # Busca todas as vacinas do pet
            cursor.execute("""
                SELECT id, NOME, PROXIMA_DOSE FROM vacina WHERE ID_PET = %s
                ORDER BY NOME
            """, (id_pet,))
            
            vacinas = cursor.fetchall()
            conn.close()
            
            if vacinas:
                return vacinas
            else:
                return []
                
        except Exception as e:
            print(f"Erro ao buscar vacinas do pet: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals():
                conn.close()
            return []
