// Получим иконку для файла
function getFileIcon(filename){
    
   
    const ext = filename.split(".").pop().toLowerCase()
    const icons = {"jpg":"🖼️", "png": "🌄", "jpeg": "🌆", "gif":"🎞️" }
    return icons[ext] || "🍱"
 }


 // Создание элемент изображения

function createImageItem(image) {
    const item = document.createElement("div");
    item.className = "image-item";
    item.dataset.id = image.id;

    const shortUrl =
        image.url.length > 50 ? image.url.substring(0, 50) + "..." : image.url;

    const icon = getFileIcon(image.name); // emoji или HTML

    // Экранируем имя файла для вставки в onclick
    const safeName = image.name.replace(/"/g, '&quot;');

    item.innerHTML = `
        <div class="image-name">
            <div class="image-icon">${icon}</div>
            <span title="${safeName}">${safeName}</span>
        </div>

        <div class="image-url-wrapper">
            <a href="${image.url}" 
               class="image-url" 
               target="_blank" 
               title="${image.url}">
                ${shortUrl}
            </a>
        </div>

        <div class="image-delete">
            <button class="delete-btn" 
                title="DELETE"
                onclick="deleteImageById(${image.id}, &quot;${safeName}&quot;)">
                🔨
            </button>
        </div>
    `;

    return item;
}
 

// Показать изображение

function showImages(){

    const images = getAllImages()
    const list = document.getElementById("images-list")
    const empty = document.getElementById("empty-state")


    if (images.length===0){
        list.innerHTML = "";
        empty.style.display = "block"
        return
    }
    empty.style.display = "none"

    list.innerHTML =  ""
    images.forEach(image =>{
        list.appendChild(createImageItem(image))

    });
 }

function deleteImageById(id){
    const list = document.getElementById("images-list")
    deleteImage(id);
    const item = document.querySelector(`[data-id="${id}"]`);
    const empty = document.getElementById("empty-state")
    console.log(item)

    if(item){
        item.style.display = "none"
        empty.style.display = "none"


    }

    
}


document.addEventListener("DOMContentLoaded", showImages)



