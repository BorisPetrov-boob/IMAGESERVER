from flask import Flask
from flask_cors import CORS
from config import Config
from utils import setup_logging, ensure_directories
from routes import register_routes 
from database import Database


def create_app():
    app = Flask(__name__)
    ## настройки приложения из config.py
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    CORS(app)
    
    with app.app_context():
    
        setup_logging()
    
    ensure_directories()
    ##Database.init_db()
    
    print("Инициализация базы данных...")
    print("Директории созданы и настроены.")
    print
    register_routes(app)
    
    return app


if __name__ == '__main__':
    print("Запуск приложения...")
    app = create_app()
    app.run(debug=Config.DEBUG)