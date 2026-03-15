const image = document.getElementById('image');
let index = 0;
let images = [];
let slideshowInterval = null;

// Меняет картинку
function changeImage() {
    if (images.length === 0) return;
    image.src = images[index];
    index = (index + 1) % images.length;
}

// Запускает слайдшоу (только один раз)
function startSlideshow() {
    if (images.length === 0) {
        console.error('No images to display');
        return;
    }

    // Первое фото
    index = 1;

    // Останавливаем прежний setInterval, если он был
    if (slideshowInterval) clearInterval(slideshowInterval);

    // Запуск нового
    slideshowInterval = setInterval(changeImage, 6000);
}

// Загружает список изображений
function loadImages() {
    fetch('images.json')
        .then(response => response.json())
        .then(data => {
            images = data;
            startSlideshow();
        })
        .catch(err => {
            console.error("Failed to load images.json", err);
        });
}

loadImages();