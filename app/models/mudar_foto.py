from app.services.s3_client import upload_foto_s3
from app.config.database import connectdb

def salvar_nova_foto(user_id, file_path):
    from ..services.s3_client import upload_foto_s3
    key = upload_foto_s3(file_path, user_id)
    
    if not key:
        return None
    
    # Atualiza no banco
    conn = connectdb()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE veterinario 
            SET imagem_perfil_veterinario = %s 
            WHERE id = %s
        """, (key, user_id))
        conn.commit()
        return key
    except Exception as e:
        print("Erro ao salvar foto no banco:", e)
        return None
    finally:
        cursor.close()
        conn.close()