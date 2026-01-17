import os
from dotenv import load_dotenv  
import logging




load_dotenv()  # Загружаем переменные окружения из .env файла

class Config:
    SECRERT_KEY = os.getenv('SECRET_KEY', 'def-key')
    DEBUG = os.getenv('DEBUG', 'False').lower()
    
    
    # Настройки загрузки файлов
    upload_folder = os.getenv("images")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}  # Исправлено: опечатка "EXTENCIONS"
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}


    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:password@localhost:5432/images_db')
    
    ##Пагинация
    ITEMS_PER_PAGE = 10
    ## папки для хранения изображений и логов
    LOGS_DIR = 'logs'
    BACKUP_DIR = 'backups'