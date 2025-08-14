import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
