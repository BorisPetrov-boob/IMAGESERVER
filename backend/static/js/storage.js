const STORAGE_KEY = 'uploaded_images';

function getAllImages() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}



function saveImage(name, URL, size) {
    try{
    
        const images = getAllImages();

        const newImage = {
        id: Date.now(),
        name: name,
        url: URL,
        size: size,
        date: new Date().toISOString()
    };


    images.push(newImage);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(images));
    return true;

    }
    catch(error){
    if (error.name === 'QuotaExceededError') {
        alert('Storage limit exceeded. Please delete some images before uploading new ones.');

    }
    return false;
   }
}

function deleteImage(id) {
    const images = getAllImages();
    const filtered = images.filter(image => image.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));

}











function filetoBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    })
}