import os
from fastapi import UploadFile
from app.config import config


def save_uploaded_file(file: UploadFile):
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(config.UPLOAD_DIR, file.filename)

    with open(file_path, 'wb') as buffer:
        buffer.write(file.file.read())

    return file_path
