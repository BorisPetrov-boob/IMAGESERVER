const iconsMap = { "jpg": "📷", "png": "🖼️", "jpeg": "🖼️", "gif": "🎞️" };
const listElement = document.getElementById("images-list");
const emptyStateElement = document.getElementById("empty-state");
const errorElement = document.getElementById("gallery-error");

function showError(message) {
    if (!errorElement) return;
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearError() {
    if (!errorElement) return;
    errorElement.textContent = '';
    errorElement.style.display = 'none';
}

function updateEmptyState() {
    if (!emptyStateElement || !listElement) return;
    const hasChildren = listElement.children.length > 0;
    emptyStateElement.style.display = hasChildren ? 'none' : 'block';
}

function getFileIcon(filename) {
    if (!filename) return "📁";
    const ext = filename.split(".").pop().toLowerCase();
    return iconsMap[ext] || "📁";
}

function createImageItem(image) {
    const item = document.createElement("div");
    item.className = "image-item";
    item.dataset.id = image.id;

    const safeName = (image.original_name || image.filename || '').replace(/"/g, '&quot;');
    const shortUrl = image.url.length > 60 ? image.url.substring(0, 60) + "..." : image.url;
    const icon = getFileIcon(image.original_name || image.filename);

    item.innerHTML = `
        <div class="image-name">
            <div class="image-icon">${icon}</div>
            <span title="${safeName}">${safeName}</span>
        </div>
        <div class="image-url-wrapper">
            <a href="${image.url}" class="image-url" target="_blank" title="${image.url}">
                ${shortUrl}
            </a>
        </div>
        <div class="image-delete">
            <button class="delete-btn" title="Delete">🗑️</button>
        </div>
    `;

    const deleteBtn = item.querySelector(".delete-btn");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", () => deleteImageById(image.id, safeName));
    }

    return item;
}

async function deleteImageById(id, name) {
    try {
        const response = await fetch(`/images/${id}`, { method: 'DELETE' });
        const payload = await response.json();

        if (!response.ok) {
            const errorMessage = payload?.error || `Unable to delete ${name}`;
            throw new Error(errorMessage);
        }

        const element = listElement.querySelector(`[data-id="${id}"]`);
        if (element) {
            element.remove();
        }

        clearError();
        updateEmptyState();
    } catch (error) {
        showError(error.message || 'Failed to delete the image.');
    }
}

async function loadImages() {
    if (!listElement) return;
    listElement.innerHTML = '';
    emptyStateElement.style.display = 'none';
    clearError();

    try {
        const response = await fetch(`/images?page=1&per_page=100`);
        const payload = await response.json();

        if (!response.ok || !payload.success) {
            throw new Error(payload.error || 'Failed to load images.');
        }

        const gallery = payload.images || [];
        if (gallery.length === 0) {
            updateEmptyState();
            return;
        }

        gallery.forEach(image => {
            const element = createImageItem(image);
            listElement.appendChild(element);
        });

        updateEmptyState();
    } catch (error) {
        showError(error.message || 'Unable to load gallery.');
        updateEmptyState();
    }
}

document.addEventListener("DOMContentLoaded", loadImages);
