import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Tuple, Optional
from config import Config
from models import Image
from utils import log_error, log_info, log_success

class Database:
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
                log_info("Database and 'images' table initialized.")
        except Exception as e:
            log_error(f"Database init error: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def save_image(image: Image, _retried: bool = False) -> Tuple[bool, Optional[int]]:
        conn = Database.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    returning id;
                """, (image.filename, image.original_name, image.size, image.file_type))
                row = cursor.fetchone()
                image_id = row["id"] if row else None
                conn.commit()
                log_success(f"Image '{image.filename}' saved to DB with ID {image_id}.")
                return True, image_id
        except Exception as e:
            message = str(e)
            if "relation \"images\" does not exist" in message and not _retried:
                log_error("Table 'images' missing. Initializing DB and retrying insert.")
                try:
                    Database.init_db()
                except Exception as init_err:
                    log_error(f"Failed to initialize database: {init_err}")
                    return False, None
                return Database.save_image(image, _retried=True)
            log_error(f"Error saving image to DB: {message}")
            return False, None
        finally:
            conn.close()

    @staticmethod
    def get_images(page: int = 1, per_page: int = 10) -> Tuple[List[Image], int]:
        try:
            conn = Database.get_connection()
        except Exception as e:
            log_error(f"DB connection error: {str(e)}")
            return [], 0
        try:
            offset = (page - 1) * per_page
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT *
                    FROM images
                    ORDER BY upload_date DESC
                    LIMIT %s OFFSET %s;
                """, (per_page, offset))
                rows = cursor.fetchall()
                images: List[Image] = []
                for row in rows:
                    images.append(Image(
                        id=row["id"],
                        filename=row["filename"],
                        original_name=row["original_name"],
                        upload_time=row.get("upload_date") or row.get("upload_time"),
                        size=row["size"],
                        file_type=row["file_type"]
                    ))
                cursor.execute("SELECT COUNT(*) as total FROM images;")
                total = cursor.fetchone()["total"]
                return images, total
        except Exception as e:
            log_error(f"Error fetching images from DB: {str(e)}")
            return [], 0
        finally:
            conn.close()

    @staticmethod
    def delete_image(image_id: int) -> Tuple[bool, Optional[str]]:
        conn = Database.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s;", (image_id,))
                row = cursor.fetchone()
                if not row:
                    log_error(f"Image with ID {image_id} not found in DB.")
                    return False
                filename = row["filename"]
                cursor.execute("DELETE FROM images WHERE id = %s;", (image_id,))
                conn.commit()
                log_success(f"Image with ID {image_id} deleted from DB.")
                return True
        except Exception as e:
            log_error(f"Error deleting image from DB: {str(e)}")
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
                        upload_date=row.get("upload_date") or row.get("upload_time"),
                        size=row["size"],
                        file_type=row["file_type"]
                    )
                return None
        except Exception as e:
            log_error(f"Error fetching image by ID: {str(e)}")
            return None
        finally:
            conn.close()
