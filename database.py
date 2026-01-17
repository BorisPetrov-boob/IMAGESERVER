import psycopg2
from psycopg2 import sql
from typing import List, Tuple, Optional
from config import Config
from models import Image
from utils import log_error, log_info, log_success


class Database():
    @staticmethod
    def get_connection():
        return psycopg2.connect(Config.DATABASE_URL)
    
    
    
    @staticmethod
    def init_db():
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    size INTEGER NOT NULL,
                    mime_type VARCHAR(50) NOT NULL
                );
            """)
            conn.commit()
            cursor.close()
            conn.close()
            log_success("База данных и таблица инициализированы успешно.")
        except Exception as e:
            log_error(f"Ошибка инициализации базы данных: {str(e)}")
    