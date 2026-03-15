const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

function showStatus(message, type) {
    const status = document.getElementById('upload-status');
    if (!status) return;

    status.textContent = message;
    status.className = `upload-status ${type}`;
    status.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => { status.style.display = 'none'; }, 5000);
    }
}

function validateFile(file) {
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        showStatus('Invalid file type. Only JPG, PNG, and GIF are allowed.', 'error');
        return false;
    }

    if (file.size > MAX_FILE_SIZE) {
        showStatus('File is too large. Maximum size is 5 MB.', 'error');
        return false;
    }

    return true;
}

async function uploadFile(file) {
    if (!file || !validateFile(file)) return;

    showStatus('Uploading...', 'info');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showStatus('File uploaded successfully!', 'success');
            
            // Заполняем поле с URL
            const urlInput = document.getElementById('current-upload-input');
            if (urlInput) {
                urlInput.value = result.image.url;
            }

            // Очищаем поле выбора файла
            const fileInput = document.getElementById('fileInput');
            if (fileInput) fileInput.value = '';

            return true;
        } else {
            showStatus('Failed to upload file: ' + result.error, 'error');
            return false;
        }

    } catch (error) {
        showStatus('Error uploading file: ' + error.message, 'error');
        return false;
    }
}

async function copyURL() {
    const urlInput = document.getElementById('current-upload-input');
    if (!urlInput || !urlInput.value) {
        showStatus('No URL to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(urlInput.value);
        showStatus('URL copied to clipboard!', 'success');

        const copyBtn = document.getElementById('copy-button');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    } catch (error) {
        showStatus('Failed to copy URL', 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData();
            const fileInput = document.getElementById('fileInput');

            if (fileInput.files.length === 0) {
                alert('Please select a file');
                return;
            }

            formData.append('file', fileInput.files[0]);

            try {
                const response = await fetch('/uploads', {  // ВАЖНО: /uploads, не /api/upload
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert('File uploaded successfully!');
                    // Обновляем галерею если нужно
                    if (typeof loadImages === 'function') {
                        loadImages();
                    }
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Upload failed');
            }
        });
    }
});