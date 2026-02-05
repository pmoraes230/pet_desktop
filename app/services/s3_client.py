import boto3
import os
from uuid import uuid4
from io import BytesIO
import mimetypes
import botocore

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
    s3 = _get_s3_client()

    extensao = file_path.split(".")[-1]
    key = f"veterinario/{user_id}_{uuid4().hex}.{extensao}"
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    try:
        s3.upload_file(file_path, BUCKET_NAME, key, ExtraArgs={"ContentType": content_type})
    except botocore.exceptions.ClientError as e:
        print("Erro ao fazer upload:", e)
        return None

    return key


def baixar_imagem_s3(key):
    s3 = _get_s3_client()
    file_obj = BytesIO()
    try:
        s3.download_fileobj(BUCKET_NAME, key, file_obj)
    except botocore.exceptions.ClientError as e:
        print("Erro ao baixar imagem:", e)
        return None

    file_obj.seek(0)
    return file_obj

def get_url_s3(key, expires_in=3600):
    """Gera URL temporária de acesso à imagem"""
    s3 = _get_s3_client()
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expires_in
        )
    except botocore.exceptions.ClientError as e:
        print("Erro ao gerar URL:", e)
        return None
    return url
