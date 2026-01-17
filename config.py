import os
from dotenv import load_dotenv  
import logging




load_dotenv()  # Загружаем переменные окружения из .env файла

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'def-key')
    DEBUG = os.getenv('DEBUG', 'False').lower()
    
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "images")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}  # Исправлено: опечатка "EXTENCIONS"
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}


    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:password@localhost:5432/images_db')
    
    ##Пагинация
    ITEMS_PER_PAGE = 10
    ## папки для хранения изображений и логов
    LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')