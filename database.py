import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Tuple, Optional
from config import Config
from models import Image
from utils import log_error, log_info, log_success


class Database():
    @staticmethod
    def get_connection():
        return psycopg2.connect(Config.DATABASE_URI)
    
    
    
    @staticmethod
    def init_db():
        conn = Database.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        original_name TEXT NOT NULL,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        size INTEGER NOT NULL,
                        file_type TEXT NOT NULL
                    );
                """)
                conn.commit()
                log_info("База данных и таблица 'images' успешно инициализированы.")
        except Exception as e:
            log_error(f"Ошибка инициализации базы данных: {str(e)}")
        finally:
            conn.close()
            
            
    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    returning id;
    """, (image.filename, image.original_name, image.size, image.file_type))
                image_id = cursor.fetchone()[0]
                conn.commit()
                log_success(f"Изображение '{image.filename}' сохранено в базе данных с ID {image_id}.")
                return True, image_id
       
        except Exception as e:
            log_error(f"Ошибка сохранения изображения в базе данных: {str(e)}")
            return False, None
        finally:
            conn.close()    
            
    @staticmethod
    def get_images(page: int=1, per_page: int=10) -> Tuple[List[Image], int]:
        conn = Database.get_connection()
        try:
            offset = (page - 1) * per_page
            
            
            with conn.cursor() as cursor:
                   
                cursor.execute("""
                    SELECT *
                    FROM images
                    ORDER BY upload_time DESC
                    LIMIT %s OFFSET %s;
                """, (per_page, offset))
                rows = cursor.fetchall()
                for row in rows:
                    images = Image(
                        id=row["id"],
                        filename=row["filename"],
                        original_name=row["original_name"],
                        upload_time=row["upload_time"],
                        size=row["size"],
                        file_type=row["file_type"]
                    )
                cursor.execute("SELECT COUNT(*) as total FROM images;")
                total = cursor.fetchone()["total"]
                return images, total
        except Exception as e:
            log_error(f"Ошибка получения изображений из базы данных: {str(e)}")
            return [], 0
        finally:
            conn.close()
            
    @staticmethod
    def delete_image(image_id: int) -> Tuple[bool, Optional[str]] :
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s;", (image_id,))
                row = cursor.fetchone()
                if not row:
                    log_error(f"Изображение с ID {image_id} не найдено в базе данных.")
                    return False
                filename = row[0]
                
                cursor.execute("DELETE FROM images WHERE id = %s;", (image_id,))
                conn.commit()
                log_success(f"Изображение с ID {image_id} удалено из базы данных.")
                return True
        except Exception as e:
            log_error(f"Ошибка удаления изображения из базы данных: {str(e)}")
            return False
        finally:
            conn.close()
            
    @staticmethod
    def get_image_by_id(image_id: int) -> Optional[Image]:
        conn = Database.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM images WHERE id = %s;
                """, (image_id,))
                row = cursor.fetchone()
                
                if row:
                    return Image(
                        id=row["id"],
                        filename=row["filename"],
                        original_name=row["original_name"],
                        upload_date=row["upload_date"],
                        size=row["size"],
                        file_type=row["file_type"]
                    )
                return None
        except Exception as e:
            log_error(f"Ошибка получения изображения по ID: {str(e)}")
            return None
        finally:
            conn.close()