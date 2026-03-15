from config import Config
from models import Image
from utils import (log_error, log_info, log_success, 
                   is_allowed_extension, save_file, delete_file, 
                   format_file_size, get_file_extension)
from database import Database
from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

def register_routes(app):
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not is_allowed_extension(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        try:
            file_data = file.read()
            file_size = len(file_data)
            
            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size = format_file_size(Config.MAX_CONTENT_LENGTH)
                return jsonify({"error": f"File size exceeds the maximum limit of {max_size}"}), 400    
            
            success, result = save_file(file.filename, file_data)
            
            if not success:
                return jsonify({"error": result}), 500
            
            new_filename = result
            file_type = get_file_extension(file.filename).replace('.', '')
            image = Image(
                filename=new_filename,
                original_name=secure_filename(file.filename),
                size=file_size,
                file_type=file_type
            )
            
            success, image_id = Database.save_image(image)
            if not success:
                delete_file(new_filename)
                return jsonify({"error": "Failed to save image metadata"}), 500
            
            log_success(f"Файл '{file.filename}' успешно загружен с ID {image_id}.")
            return jsonify({
                "success": True, 
                "message": "File uploaded successfully", 
                "image": {
                    "id": image_id,
                    "filename": new_filename,
                    "original_name": file.filename,
                    "size": format_file_size(file_size),
                    "url": f"/api/images/{new_filename}"
                }
            }), 201
        except Exception as e:
            log_error(f"Ошибка при загрузке файла: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/images/<filename>')
    def serve_image(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route('/api/images', methods=['GET'])
    def get_images():
        """Получение списка всех изображений"""
        try:
            images, total = Database.get_images()
            
            response_data = {
                "success": True,
                "images": [image.to_dict() for image in images],
                "total": total
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            log_error(f"Ошибка при получении списка изображений: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/images/<int:image_id>', methods=['DELETE'])
    def delete_image(image_id):
        """Удаление изображения по ID"""
        try:
            success = Database.delete_image(image_id)
            
            if success:
                log_success(f"Изображение с ID {image_id} успешно удалено")
                return jsonify({
                    "success": True,
                    "message": f"Image with ID {image_id} deleted successfully"
                }), 200
            else:
                return jsonify({"error": "Image not found"}), 404
                
        except Exception as e:
            log_error(f"Ошибка при удалении изображения: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok", "service": "image-api"})