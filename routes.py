from config import Config
from models import Image
from utils import (log_error, 
                   log_info, log_success, 
                   is_allowed_extension,
                   is_valid_file_size, save_file, delete_file, save_file, format_file_size, get_file_extension

)
from database import Database
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename




def register_routes(app):
    ### Регистрация маршрутов Flask приложения
    @app.route('/')
    def index():
        return render_template("index.html")
    
    
    @app.route('/uploads', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 
        
        if not is_allowed_extension(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        try:
            file_data = file.read()
            file_size = len(file_data)
            
            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size = format_file_size(Config.MAX_CONTENT_LENGTH)
                return jsonify({"error": f"File size exceeds the maximum limit of {max_size}"}), 400    
            success,result = save_file(file_data, file.filename
                                       )
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
                        "url": f"/images/{new_filename}",
                        "delete_url": f"/images/{image_id}"
                }
            }), 201
        except Exception as e:
            log_error(f"Ошибка при загрузке файла: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


    @app.route('/images/<filename>')
    def serve_image(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route('/images', methods=['GET'])
    def get_images():
        """Получение списка всех изображений с пагинацией"""
        try:
            # Получаем параметры пагинации из запроса
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', Config.ITEMS_PER_PAGE, type=int)
            
            # Получаем изображения из базы данных
            images, total = Database.get_images(page, per_page)
            
            # Формируем ответ
            response_data = {
                "success": True,
                "images": [image.to_dict() for image in images],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
                }
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            log_error(f"Ошибка при получении списка изображений: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/images/<int:image_id>', methods=['GET'])
    def get_image_by_id(image_id):
        """Получение информации об изображении по ID"""
        image = Database.get_image_by_id(image_id)
        if image:
            return jsonify({"success": True, "image": image.to_dict()}), 200
        else:
            return jsonify({"error": "Image not found"}), 404

    @app.route('/images/<int:image_id>', methods=['DELETE'])
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