from ..models.agendamento_model import AgendamentoModel
from datetime import datetime, date, timedelta
import uuid


class AgendamentoController:
    def __init__(self, vet_id=None):
        self.vet_id = vet_id
        self.model = AgendamentoModel()

    def listar_pets(self, id_veterinario=None):
        """Lista apenas pets aceitos pelo veterinario logado."""
        vet_id = id_veterinario if id_veterinario is not None else self.vet_id
        if not vet_id:
            return []
        return self.model.listar_pets_aceitos(vet_id)

    def listar_veterinarios(self):
        """Lista todos os veterinarios."""
        return self.model.listar_veterinarios()

    def criar_agendamento(self, id_pet, id_veterinario, data, horario, tipo_consulta, observacoes):
        """Cria um retorno confirmado para um pet ja aceito pelo veterinario."""
        if not id_veterinario:
            print("Erro ao criar agendamento: veterinario nao informado")
            return False

        try:
            data_consulta = datetime.strptime(data, "%Y-%m-%d").date() if isinstance(data, str) else data
            datetime.strptime(horario, "%H:%M") if isinstance(horario, str) else horario
        except Exception:
            print("Erro ao criar agendamento: data ou horario invalido")
            return False

        if data_consulta < date.today():
            print("Erro ao criar agendamento: nao e possivel marcar retorno em data passada")
            return False

        tipo_consulta = tipo_consulta or "Retorno"
        observacoes = (observacoes or "")[:255]
        retorno_agendado = data if tipo_consulta == "Retorno" else None
        id_consulta = uuid.uuid4().hex

        return self.model.criar_agendamento(
            id_consulta,
            id_pet,
            id_veterinario,
            data,
            horario,
            tipo_consulta,
            observacoes,
            retorno_agendado,
        )

    def liberar_horarios(self, id_veterinario, data, hora_inicio, hora_fim, intervalo_minutos=30):
        """Cria horarios livres na agenda_disponivel para o veterinario."""
        try:
            if not id_veterinario:
                print("Erro ao liberar horarios: veterinario logado nao informado")
                return 0

            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fim = datetime.strptime(hora_fim, "%H:%M")
            if inicio >= fim:
                print("Erro ao liberar horarios: hora inicial deve ser menor que hora final")
                return 0

            intervalo_minutos = int(intervalo_minutos)
            if intervalo_minutos <= 0:
                return 0

            horarios = []
            atual = inicio
            while atual < fim:
                horarios.append(atual.strftime("%H:%M"))
                atual += timedelta(minutes=intervalo_minutos)

            return self.model.liberar_horarios(id_veterinario, data, horarios)
        except Exception as e:
            print(f"Erro ao liberar horarios: {e}")
            return 0
