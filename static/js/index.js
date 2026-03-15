const sliderImage = document.getElementById('image');
let images = [];
let slideshowInterval = null;

function rotateAndShow() {
    if (!sliderImage || images.length === 0) return;
    const next = images.shift();
    sliderImage.src = next;
    images.push(next);
}

function startSlideshow() {
    if (!sliderImage || images.length === 0) {
        console.warn('No images to display for the slideshow.');
        return;
    }
    rotateAndShow();
    if (slideshowInterval) clearInterval(slideshowInterval);
    slideshowInterval = setInterval(rotateAndShow, 6000);
}

async function loadImages() {
    if (!sliderImage) return;
    try {
        const response = await fetch('/images/random');
        const data = await response.json();
        images = Array.isArray(data.images) ? data.images.filter(Boolean) : [];
        if (!images.length) {
            const fallback = sliderImage.dataset.placeholder || sliderImage.src;
            images = fallback ? [fallback] : [];
        }
        startSlideshow();
    } catch (error) {
        console.error('Failed to load images for slideshow', error);
    }
}

document.addEventListener('DOMContentLoaded', loadImages);
