import os
from dotenv import load_dotenv

load_dotenv()

# App Configuration


class Config:
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", 'uploads/')


config = Config()
