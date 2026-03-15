const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];
let uploadedUrl = '';

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

        const response = await fetch('/uploads', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            uploadedUrl = result.image?.url || '';
            const urlInput = document.getElementById('current-upload-input');
            if (urlInput) {
                urlInput.value = uploadedUrl;
            }

            showStatus('File uploaded successfully!', 'success');

            const fileInput = document.getElementById('fileInput');
            if (fileInput) fileInput.value = '';
        } else {
            showStatus('Failed to upload file: ' + (result.error || 'unknown error'), 'error');
        }
    } catch (error) {
        const message = error && error.message ? error.message : String(error);
        showStatus('Error uploading file: ' + message, 'error');
    }
}

async function copyURL() {
    if (!uploadedUrl) {
        showStatus('No URL to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(uploadedUrl);
        showStatus('URL copied to clipboard!', 'success');

        const copyBtn = document.getElementById('copy-button');
        if (copyBtn) {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        }
    } catch (error) {
        showStatus('Failed to copy URL', 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browse-btn');
    const copyBtn = document.getElementById('copy-button');

    if (dropArea) {
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('dragover');
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
                uploadFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target && e.target.files && e.target.files[0]) {
                uploadFile(e.target.files[0]);
            }
        });

        if (browseBtn) {
            browseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                fileInput.click();
            });
        }
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', copyURL);
    }
});
