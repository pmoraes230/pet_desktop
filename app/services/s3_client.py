import boto3
import os
from uuid import uuid4
from io import BytesIO

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_S3_REGION_NAME")
BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )


def upload_foto_s3(file_path, user_id):
    """Faz upload da foto para o S3 e retorna a KEY salva no banco"""
    s3 = _get_s3_client()

    extensao = file_path.split(".")[-1]
    key = f"veterinario/{user_id}_{uuid4().hex}.{extensao}"

    s3.upload_file(
        file_path,
        BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "image/jpeg"}
    )

    return key


def baixar_imagem_s3(key):
    """Baixa a imagem do S3 e retorna em memória (BytesIO)"""
    s3 = _get_s3_client()

    file_obj = BytesIO()
    s3.download_fileobj(BUCKET_NAME, key, file_obj)
    file_obj.seek(0)

    return file_obj
