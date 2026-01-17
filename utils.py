import os 
import uuid
import logging
from werkzeug.utils import secure_filename
from config import Config



## Локальные константы из config.py
def setup_logging():
    ## Настройка логирования
    log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format, 
        datefmt=date_format,
        handlers =[
            logging.FileHandler(Config.LOGS_DIR, encoding='utf-8'),
            logging.StreamHandler()
       ]
    )
    
    
    
def log_info(message):
    logging.info(message)
## логирование информационных сообщений
def log_error(message):
    logging.error(message)
## логирование ошибок

def log_success(message):
    logging.info(f"SUCCESS: {message}")
    
## работа с файлами
def ensure_directories():
    os.makedirs(Config.upload_folder, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    
    
## Валидатор файлов
def get_file_extension(filename):
## Получение расширения файла
   return os.path.splitext(filename)[1].lower()
def is_allowed_extension(filename):
   ext = get_file_extension(filename)
   return ext in Config.ALLOWED_EXTENSIONS


def is_valid_file_size(file_size):
   return 0 < file_size <= Config.MAX_CONTENT_LENGTH
def format_file_size(size_bytes):
    ## Формирует размер файла для отображения
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    

def generate_unique_filename(original_filename):
    ## Генерация уникального имени файла
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"

def save_file(filename, file_content):
    try:
        original_name = secure_filename(filename)
        new_filename = generate_unique_filename(original_name)
        file_path = os.path.join(Config.upload_folder, new_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)
            log_success(f"Файл сохранен: {new_filename} (оригинальное имя: {original_name})")
        return True, new_filename
    except Exception as error:
        error_msg = f"Ошибка при сохранении файла: {str(error)}"
        log_error(error_msg)
        return False, error_msg
    
    
     
    
def delete_file(filename):
    try:
        file_path =  os.path.join(Config.upload_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False    
        
    except Exception as e:
                print(f"Ошибка при удалении файла: {str(e)}")
                return False
