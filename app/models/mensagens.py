from ..config.database import connectdb
import uuid

def buscar_mensagens_conversa(id_tutor: str, id_veterinario: str):
    """
    Retorna todas as mensagens entre um tutor e um veterinário, ordenadas por data.
    """
    conn = None
    cursor = None
    try:
        conn = connectdb()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                id,
                CONTEUDO,
                DATA_ENVIO,
                ENVIADO_POR,
                LIDA,
                ID_TUTOR,
                ID_VETERINARIO
            FROM mensagem
            WHERE ID_TUTOR = %s
                AND ID_VETERINARIO = %s
            ORDER BY DATA_ENVIO ASC;
        """

        cursor.execute(query, (id_tutor, id_veterinario))
        result = cursor.fetchall()

        return result if result else [] 
    
    except Exception as e:
        print(f"Erro ao buscar mensagens: {str(e)}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def salvar_mensagem(conteudo: str, enviado_por: str, id_tutor: str, id_veterinario: str) -> dict:
    """
    Salva uma nova mensagem no banco de dados.
    """

    conn = None
    cursor = None
    try:
        conn = connectdb()
        cursor = conn.cursor()

        novo_id = str(uuid.uuid4()).replace("-", "")
        query = """
            INSERT INTO mensagem 
                (id, CONTEUDO, DATA_ENVIO, ENVIADO_POR, LIDA, ID_TUTOR, ID_VETERINARIO)
            VALUES 
                (%s, %s, NOW(), %s, FALSE, %s, %s);
                """
        cursor.execute(query, (novo_id, conteudo, enviado_por, id_tutor, id_veterinario))
        conn.commit()

        cursor.execute("""
            SELECT * FROM mensagem WHERE id = %s;
        """, (novo_id,))
        regitro = cursor.fetchone()
        return regitro if regitro else {}
    except Exception as e:
        print(f"Erro ao salvar mensagem: {str(e)}")
        if conn:
            conn.rollback()
        return {}

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def marcar_mensagens_como_lidas(id_tutor: str, id_veterinario: str) -> bool:
    """
    Marca todas as mensagens da conversa como lidas (útil quando o usuário abre o chat).
    """
    conn = None
    cursor = None
    try:
        conn = connectdb()
        cursor = conn.cursor()

        query = """
            UPDATE mensagem
               SET LIDA = TRUE
             WHERE ID_TUTOR = %s
               AND ID_VETERINARIO = %s
               AND LIDA = FALSE
               AND ENVIADO_POR != %s;   -- não marca as próprias mensagens como não lidas
        """

        # Se for tutor abrindo → marca mensagens do veterinário
        # Se for vet abrindo   → marca mensagens do tutor
        enviado_por_oposto = "VETERINARIO" if id_tutor else "TUTOR"  # ajuste conforme quem chama

        cursor.execute(query, (id_tutor, id_veterinario, enviado_por_oposto))
        conn.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print(f"Erro ao marcar mensagens como lidas: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()