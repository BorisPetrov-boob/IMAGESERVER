import datetime
import os
import uuid

from flask import Flask, send_from_directory, jsonify, request
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='')

# Конфигурация
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['ALLOWED_EXTENSIONS'] = {'.jpg', '.jpeg', '.png', '.gif'}

# Создаем папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# API маршруты
@app.route('/uploads', methods=['POST'])
def upload_file():
    try:
        print("=== UPLOAD REQUEST RECEIVED ===")
        print(f"Files in request: {request.files}")
        print(f"Form data: {request.form}")

        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        print(f"File received: {file.filename}")

        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            print(f"ERROR: File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed'}), 400

        # Создаем безопасное имя файла с уникальным ID
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        # Путь для сохранения
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # ВАЖНО: Используем save() метод Flask, который правильно обрабатывает байты
        file.save(file_path)
        print(f"File saved successfully: {file_path}")

        # Получаем размер файла
        file_size = os.path.getsize(file_path)

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_filename': original_filename,
            'url': f'/uploads/{unique_filename}',
            'size': file_size,
            'message': 'File uploaded successfully'
        }), 200

    except Exception as e:
        print(f"ERROR in upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500