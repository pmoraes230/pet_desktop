from ..config.database import connectdb, closedb
from datetime import datetime
import uuid

class AgendamentoController:
    def __init__(self):
        pass

    def listar_pets(self):
        """Lista todos os pets"""
        try:
            conn = connectdb()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, nome FROM pet LIMIT 100"
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
            query = "SELECT id, nome FROM vet_user LIMIT 100"
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
            conn = connectdb()
            cursor = conn.cursor()
            
            # Gera UUID sem hífens (32 caracteres) para caber no campo char(32)
            id_consulta = str(uuid.uuid4()).replace("-", "")
            
            query = """
                INSERT INTO consulta 
                (id, ID_PET, ID_VETERINARIO, DATA_CONSULTA, HORARIO_CONSULTA, TIPO_DE_CONSULTA, OBSERVACOES, STATUS)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'agendado')
            """
            
            cursor.execute(query, (id_consulta, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes))
            conn.commit()
            closedb(conn)
            print(f"Agendamento criado com sucesso! ID: {id_consulta}")
            return True
        except Exception as e:
            print(f"Erro ao criar agendamento: {e}")
            return False