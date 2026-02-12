from datetime import datetime
import calendar

class AgendaUtils:
    @staticmethod
    def formatar_data(numero_dia, mes, ano):
        """Formata a data para string"""
        return f"{ano}-{mes:02d}-{numero_dia:02d}"
    
    @staticmethod
    def eh_hoje(numero_dia, mes, ano):
        """Verifica se é hoje"""
        hoje = datetime.now()
        return (numero_dia == hoje.day and 
                mes == hoje.month and 
                ano == hoje.year)
    
    @staticmethod
    def obter_proximo_mes(mes, ano):
        """Retorna próximo mês e ano"""
        if mes == 12:
            return 1, ano + 1
        return mes + 1, ano
    
    @staticmethod
    def obter_mes_anterior(mes, ano):
        """Retorna mês anterior e ano"""
        if mes == 1:
            return 12, ano - 1
        return mes - 1, ano
    
    @staticmethod
    def calcular_primeira_semana(mes, ano):
        """Retorna primeiro dia da semana e número de dias do mês"""
        return calendar.monthrange(ano, mes)