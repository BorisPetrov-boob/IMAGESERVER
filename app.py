import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import uuid
import json
from email import policy
from email.parser import BytesParser


HOST = 'localhost'  # Исправлено: убрана лишняя кавычка
PORT = 8000
IMAGE_DIR = 'images'
LOGS_DIR = 'logs'

MAX_FILE_SIZE = 5 * 1024 * 1024  # Исправлено: убрано подчеркивание
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}  # Исправлено: опечатка "EXTENCIONS"
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}



LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

def setup_logging():
    ## Настройка логирования
    log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format, 
        datefmt=date_format,
        handlers =[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
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
## логирование успешных операций




def ensure_directories():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


## Валидатор файлов
def get_file_extension(filename):
## Получение расширения файла
   return os.path.splitext(filename)[1].lower()
def is_allowed_extension(filename):
   ext = get_file_extension(filename)
   return ext in ALLOWED_EXTENSIONS


def is_valid_file_size(file_size):
   return 0 < file_size <= MAX_FILE_SIZE
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


def validate_file(filename, file_size):
    ## Валидация файла
    if not is_allowed_extension(filename):
        ext = get_file_extension(filename)
        return False, f"Не поддерживаемый формат файла: {ext}" 
    if not is_valid_file_size(file_size):
        if file_size <= 0:
            return False, "Файл пустой"
        else:
            max_size_formatted = format_file_size(MAX_FILE_SIZE)
            actual_size_formatted = format_file_size(file_size)
            return False, f"Превышен максимальный размер файла: {actual_size_formatted} (макс: {max_size_formatted})"
    return True, "Файл валиден"



## Парсинг мультипарт формы

def parse_multipart_form_data(content_type, body):
    ## парсит multipart/form-data и извлекает файил
    ## возвращает (file_content, filename) или (None, error_message) при ошибке


    try:
        if 'multipart/form-data' not in content_type:
            return None, "Invalid content type"
        headers = f'Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n'.encode()
        msg = BytesParser(policy=policy.default).parsebytes(headers + body)
        
        if not msg.is_multipart():
            return None, "Not a multipart message"
        
        for part in msg.iter_parts():
            if part.get_content_disposition() != 'form-data':
                continue
            if part.get_param('name', headers="content-disposition") != 'file':
                continue
            filename = part.get_filename()
            if not filename:
                continue
            file_content = part.get_payload(decode=True)
            return filename, file_content
        return None, "File part not found"
    except Exception as error:
        return None, f"Error parsing multipart data: {str(error)}"
        

    
def save_file(filename, file_content):
    try:
        new_filename = generate_unique_filename(filename)
        file_path = os.path.join(IMAGE_DIR, new_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)
            log_success(f"Файл сохранен: {new_filename}")
        return True, new_filename
    except Exception as error:
        error_msg = f"Ошибка при сохранении файла: {str(error)}"
        log_error(error_msg)
        return False, error_msg


  


class ImageServerHandler(BaseHTTPRequestHandler):
    ## Обрабочик HTTP запросов
    def do_GET(self):
        ## Обработка GET запросов
        if self.path == '/':
            self.log("Serving welcome page")
            self.send_welcome_page()
        else:
            self.send_error_response(404, "Not Found")



def do_POST(self):
        ## Обработка POST запросов
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_error_response(404, "Not Found")



def handle_upload(self):
    try:
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
    
        if content_length > MAX_FILE_SIZE:
            self.log("File size exceeds maximum limit", level='error')
            self.send_error_response(413, "File size exceeds maximum limit")
            return
        
        body = self.rfile.read(content_length)
        filename, file_content = parse_multipart_form_data(content_type, body)
        if not filename or file_content is None:
            self.log("Invalid multipart/form-data", level='error')
            self.send_error_response(400, "Invalid multipart/form-data")
            return
        
        is_valid, error_message = validate_file(filename, file_content)
        if not is_valid:
            self.log(f"File validation failed: {error_message}", level='error')
            self.send_error_response(400, error_message)
            return
        
        success, result = save_file(filename, file_content)
        if success:
            new_filename = result
            file_url = f"images/{new_filename}"
            self.log(f"File uploaded successfully: {new_filename}")
            response_data = {
                "success": True,
                "message": "File uploaded successfully",
                "filename": new_filename,
                "original_filename": filename,
                "size": format_file_size(len(file_content)),
                "url": file_url
            }
            self.send_json_response(201, response_data)
        else:
            error_msg = result
            self.log(f"File upload failed: {error_msg}", level='error')
            self.send_error_response(500, error_msg)
    
    except Exception as error:
        error_msg = f"Unexpected error during upload: {str(error)}"
        self.log(error_msg, level='error')
        self.send_error_response(500, error_msg)



    def send_welcome_page(self):
        message = {
            "message": "Welcome to the Image Upload Server!",
            "endpoints": {
                "GET /": "Welcome page",
                "POST /upload": "Upload an image"
            },
            "info": {
                "max_file_size": "5MB",
                "allowed_formats": list(ALLOWED_EXTENSIONS)
            }
        }

        self.send_json_response(200, message)


    def log(self, message, level='info'):
    ## Универсальная функция логирования
        client_ip = self.client_address[0]
        log_message = f"{client_ip} - {self.command} -{self.path} - {message}"
        
        if level == 'error':
            log_error(log_message)
        else:
            log_info(log_message)
            




    def send_json_response(self, status_code, data):
        ## Отправка JSON ответа
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        
        repsonse = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(repsonse.encode('utf-8'))

    def send_error_response(self, status_code, message):
        ## Отправка ошибки
        error_data = {
            "error": {
                "error": message,
                "status_code": status_code
            }
    }
        self.send_json_response(status_code, error_data)

if __name__ == '__main__':
    ensure_directories()

    setup_logging()
   
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ImageServerHandler)
    httpd.serve_forever()
