# src/models/tutores.py
from ..config.database import connectdb

def listar_tutores_para_veterinario(vet_id: str = None) -> list[dict]:
    """
    Se vet_id for passado → tutores que já consultaram com esse vet
    Se vet_id for None → retorna todos os tutores (como Tutor.objects.all())
    """
    conn = None
    cursor = None
    try:
        conn = connectdb()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT DISTINCT 
                t.id,
                t.nome_tutor,
                COALESCE(t.imagem_perfil_tutor, '🐶') AS avatar
            FROM tutor t
            INNER JOIN mensagem m ON m.ID_TUTOR = t.id
            WHERE m.ID_VETERINARIO = %s
            ORDER BY t.nome_tutor ASC
            LIMIT 100;
        """

        cursor.execute(query, (vet_id,))
        return cursor.fetchall() or []

    except Exception as e:
        print(f"Erro ao listar tutores: {str(e)}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()