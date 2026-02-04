from app.services.s3_client import upload_foto_s3
from app.config.database import connectdb

def salvar_nova_foto(user_id, file_path):
    try:
        # Upload para o S3
        key = upload_foto_s3(file_path, user_id)

        # Salva caminho da imagem no banco
        conn = connectdb()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE veterinario SET imagem_perfil_veterinario=%s WHERE id=%s",
            (key, user_id)
        )
        conn.commit()
        conn.close()

        return key  # 👈 importante retornar a key

    except Exception as e:
        print("Erro ao salvar nova foto:", e)
        return None
