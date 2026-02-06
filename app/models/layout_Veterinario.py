from ..config.database import connectdb

def dados_perfil_veterinario(perfil_id):
    """Recupera os dados do veterinário e os pets atendidos"""
    conn = None
    cursor = None
    try:
        conn = connectdb()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                v.id AS veterinario_id,
                v.NOME AS nome_veterinario,
                p.id AS pet_id,
                p.NOME AS nome_pet,
                p.ESPECIE,
                p.RACA,
                p.SEXO
            FROM veterinario v
            INNER JOIN consulta c 
                ON c.ID_VETERINARIO = v.id
            INNER JOIN pet p 
                ON p.id = c.ID_PET
            WHERE v.id = %s;
        """

        cursor.execute(query, (perfil_id,))
        result = cursor.fetchall()  # vários pets

        return result if result else []

    except Exception as e:
        print(f"Erro ao recuperar dados do perfil: {str(e)}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
