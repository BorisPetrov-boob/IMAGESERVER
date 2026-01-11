import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import uuid
import json


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


class ImageServerHandler(BaseHTTPRequestHandler):
    ## Обрабочик HTTP запросов
    def do_GET(self):
        ## Обработка GET запросов
        if self.path == '/':
            self.log("Serving welcome page")
            self.send_welcome_page()
        else:
            self.send_error_response(404, "Not Found")


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
