from ..models.agenda_model import AgendaModel
from datetime import datetime, date, timedelta
import calendar
import unicodedata


class AgendaController:
    def __init__(self, id_veterinario=None, vet_id=None):
        self.id_veterinario = id_veterinario if id_veterinario is not None else vet_id
        self.vet_id = self.id_veterinario
        self.model = AgendaModel()

    def _como_data(self, valor):
        if not valor:
            return None
        if hasattr(valor, "date"):
            return valor.date()
        return valor

    def _status_normalizado(self, status):
        texto = (status or "").lower().replace("Ã­", "i").replace("ÃƒÂ­", "i")
        return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

    def buscar_consultas_do_dia(self, numero_dia, mes, ano):
        """Busca consultas do veterinario para um dia especifico."""
        data_consulta = f"{ano}-{mes:02d}-{numero_dia:02d}"
        return self.model.buscar_consultas_do_dia(data_consulta, self.id_veterinario)

    def buscar_consultas_da_semana(self, data_inicial_semana):
        """Busca consultas do veterinario entre domingo e sabado."""
        if not data_inicial_semana:
            return []

        data_inicio = data_inicial_semana.date()
        data_fim = (data_inicial_semana + timedelta(days=6)).date()
        return self.model.buscar_consultas_da_semana(data_inicio, data_fim, self.id_veterinario)

    def buscar_consultas_do_mes(self, mes, ano):
        """Busca consultas do veterinario no mes."""
        return self.model.buscar_consultas_do_mes(mes, ano, self.id_veterinario)

    def dias_com_consultas(self, mes, ano):
        consultas = self.buscar_consultas_do_mes(mes, ano)
        return {
            self._como_data(consulta["DATA_CONSULTA"]).day
            for consulta in consultas
            if consulta.get("DATA_CONSULTA")
        }

    def datas_com_consultas_do_mes(self, mes, ano):
        """Retorna as datas do mes que possuem consulta."""
        consultas = self.buscar_consultas_do_mes(mes, ano)
        return {
            self._como_data(consulta.get("DATA_CONSULTA"))
            for consulta in consultas
            if consulta.get("DATA_CONSULTA")
        }

    def resumo_calendario_mes(self, mes, ano):
        """Monta o backend do calendario completo, com semanas domingo-sabado."""
        consultas = self.buscar_consultas_do_mes(mes, ano)
        contagem_por_data = {}

        for consulta in consultas:
            data_consulta = self._como_data(consulta.get("DATA_CONSULTA"))
            if not data_consulta:
                continue
            contagem_por_data[data_consulta] = contagem_por_data.get(data_consulta, 0) + 1

        semanas = []
        for semana in calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes):
            semanas.append([
                {
                    "data": dia,
                    "dia": dia.day,
                    "fora_do_mes": dia.month != mes,
                    "tem_consulta": dia in contagem_por_data,
                    "total_consultas": contagem_por_data.get(dia, 0),
                }
                for dia in semana
            ])

        return {
            "mes": mes,
            "ano": ano,
            "semanas": semanas,
            "datas_com_consulta": set(contagem_por_data.keys()),
            "total_consultas": sum(contagem_por_data.values()),
        }

    def dias_com_consultas_na_semana(self, data_inicial_semana):
        try:
            if not data_inicial_semana:
                return set()

            consultas = self.buscar_consultas_da_semana(data_inicial_semana)
            inicio = data_inicial_semana.date()
            fim = (data_inicial_semana + timedelta(days=7)).date()

            dias_semana = set()
            for consulta in consultas:
                data_consulta = self._como_data(consulta.get("DATA_CONSULTA"))
                if data_consulta and inicio <= data_consulta < fim:
                    dias_semana.add(data_consulta)

            return dias_semana
        except Exception as e:
            print(f"Erro ao buscar dias com consultas na semana: {e}")
            return set()

    def liberar_horarios(self, data_str, hora_inicio_str, hora_fim_str, duracao_slot):
        """Cria vagas livres na agenda do veterinario."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado.", 0, 0

        try:
            duracao_slot = int(duracao_slot)
            if duracao_slot not in (15, 30, 45, 60):
                return False, "Intervalo invalido.", 0, 0

            data_vaga = datetime.strptime(data_str, "%d/%m/%Y").date()
            inicio = datetime.strptime(f"{data_str} {hora_inicio_str}", "%d/%m/%Y %H:%M")
            fim = datetime.strptime(f"{data_str} {hora_fim_str}", "%d/%m/%Y %H:%M")

            if data_vaga < date.today():
                return False, "Nao e possivel liberar horarios em uma data passada.", 0, 0

            if fim <= inicio:
                return False, "A hora de termino deve ser maior que a hora de inicio.", 0, 0

            horarios = []
            atual = inicio
            while atual < fim:
                horarios.append(atual.time())
                atual += timedelta(minutes=duracao_slot)

            return self.model.salvar_horarios_liberados(self.id_veterinario, data_vaga, horarios)
        except Exception as e:
            return False, f"Erro ao liberar horarios: {e}", 0, 0

    def atualizar_status_consulta(self, consulta_id, novo_status):
        """Atualiza o status da consulta e sincroniza o slot quando necessario."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado."

        consulta = self.model.buscar_consulta_do_vet(consulta_id, self.id_veterinario)
        if not consulta:
            return False, "Consulta nao encontrada."

        novo_status_normalizado = self._status_normalizado(novo_status)
        status_atual = self._status_normalizado(consulta.get("STATUS"))

        if novo_status_normalizado in ("confirmado", "cancelado") and status_atual != "pendente":
            return False, f"Status atual: {consulta.get('STATUS')}. Nao e possivel alterar."

        if novo_status_normalizado == "concluido" and status_atual != "confirmado":
            return False, f"Status atual: {consulta.get('STATUS')}. Nao e possivel finalizar."

        status_vaga = None
        if novo_status == "Confirmado":
            status_vaga = "Ocupado"
        elif novo_status == "Cancelado":
            status_vaga = "Livre"

        sucesso, mensagem, _ = self.model.atualizar_status_consulta(
            consulta_id,
            self.id_veterinario,
            novo_status,
            status_vaga,
        )
        return sucesso, mensagem

    def excluir_consulta(self, consulta_id):
        """Remove uma consulta do veterinario e libera a vaga correspondente."""
        if not self.id_veterinario:
            return False, "Veterinario nao identificado."

        return self.model.excluir_consulta(consulta_id, self.id_veterinario)
