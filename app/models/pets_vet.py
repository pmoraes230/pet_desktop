from ..config.database import connectdb
from uuid import uuid4
import uuid
class PetAll:

    # =========================
    # PETS
    # =========================

    @staticmethod
    def listar_pets():
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, NOME, ESPECIE, RACA, DATA_NASCIMENTO,
                       SEXO, PESO, CASTRADO, PERSONALIDADE,
                       IMAGEM, ID_TUTOR
                FROM pet
                ORDER BY NOME
            """)

            pets = cursor.fetchall()
            conn.close()
            return pets if pets else []

        except Exception as e:
            print(f"Erro ao listar pets: {e}")
            if 'conn' in locals():
                conn.close()
            return []

    @staticmethod
    def buscar_pet(id_pet):
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, NOME, ESPECIE, RACA, DATA_NASCIMENTO,
                       SEXO, PESO, CASTRADO, PERSONALIDADE,
                       IMAGEM, ID_TUTOR
                FROM pet
                WHERE id = %s
            """, (id_pet,))

            pet = cursor.fetchone()
            conn.close()
            return pet if pet else {}

        except Exception as e:
            print(f"Erro ao buscar pet: {e}")
            return {}

    @staticmethod
    def atualizar_imagem_pet(id_pet, imagem_key):
        try:
            conn = connectdb()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE pet
                SET IMAGEM = %s
                WHERE id = %s
            """, (imagem_key, id_pet))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Erro ao atualizar imagem: {e}")
            return False

    # =========================
    # TUTOR
    # =========================

    @staticmethod
    def buscar_tutor_por_pet_id(id_pet):
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT ID_TUTOR FROM pet WHERE id = %s", (id_pet,))
            pet = cursor.fetchone()

            if not pet or not pet.get("ID_TUTOR"):
                conn.close()
                return {}

            cursor.execute("SELECT * FROM tutor WHERE id = %s", (pet["ID_TUTOR"],))
            tutor = cursor.fetchone()

            conn.close()
            return tutor if tutor else {}

        except Exception as e:
            print(f"Erro ao buscar tutor: {e}")
            return {}

    # =========================
    # VACINAS (AUTO_INCREMENT)
    # =========================

    @staticmethod
    def buscar_vacinas_por_pet_id(id_pet):
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, NOME, PROXIMA_DOSE
                FROM vacina
                WHERE ID_PET = %s
                ORDER BY PROXIMA_DOSE DESC
            """, (id_pet,))

            vacinas = cursor.fetchall()
            conn.close()
            return vacinas if vacinas else []

        except Exception as e:
            print(f"Erro ao buscar vacinas: {e}")
            return []



    @staticmethod
    def adicionar_medicamento(id_pet, nome, dosagem, frequencia, inicio, termino):
        try:
            conn = connectdb()
            cursor = conn.cursor()

            medicamento_id = uuid4().hex  # 🔥 GERA UUID

            observacao = f"Dosagem: {dosagem} | Frequência: {frequencia}"
            horario_db = frequencia if ":" in str(frequencia) else "08:00:00"

            cursor.execute("""
                INSERT INTO medicamento
                (id, ID_PET, NOME, HORARIO, DATA_INICIO, DATA_FIM, OBSERVACOES)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                medicamento_id,   # 🔥 AQUI ESTÁ A CORREÇÃO
                id_pet,
                nome,
                horario_db,
                inicio,
                termino,
                observacao
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Erro ao adicionar medicamento: {e}")
            return False

        # =========================
        # MEDICAMENTOS (AUTO_INCREMENT)
        # =========================

    @staticmethod
    def buscar_medicamentos(id_pet):
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id,
                       NOME,
                       TIME_FORMAT(HORARIO, '%H:%i') as HORARIO,
                       DATA_INICIO,
                       DATA_FIM,
                       OBSERVACOES
                FROM medicamento
                WHERE ID_PET = %s
                ORDER BY DATA_INICIO DESC
            """, (id_pet,))

            meds = cursor.fetchall()
            conn.close()
            return meds if meds else []

        except Exception as e:
            print(f"Erro ao buscar medicamentos: {e}")
            return []

    

    # =========================
    # DIÁRIO EMOCIONAL
    # =========================

    @staticmethod
    def buscar_historico_emocional(id_pet):
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    HUMOR as nivel,
                    DATE_FORMAT(DATA_REGISTRO, '%d/%m') as data,
                    RELATO as nota
                FROM diario_emocional
                WHERE ID_PET = %s
                ORDER BY DATA_REGISTRO ASC
                LIMIT 7
            """, (id_pet,))

            dados = cursor.fetchall()
            conn.close()
            return dados if dados else []

        except Exception as e:
            print(f"Erro ao buscar emocional: {e}")
            return []
        
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()    