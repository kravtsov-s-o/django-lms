// Функция для преобразования строки в slug
function slugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')           // Преобразование пробелов в дефисы
        .replace(/[^\w\-]+/g, '')       // Удаление всех не буквенно-цифровых символов
        .replace(/\-\-+/g, '-')         // Удаление повторяющихся дефисов
        .replace(/^-+/, '')             // Удаление дефисов в начале строки
        .replace(/-+$/, '');            // Удаление дефисов в конце строки
}

document.addEventListener('DOMContentLoaded', function() {
    var titleInput = document.querySelector('#id_title');  // Поле title
    var slugInput = document.querySelector('#id_slug');    // Поле slug
    var timeout = null;

    // Автоматически генерируем slug при изменении поля title с задержкой
    if (titleInput && slugInput) {
        titleInput.addEventListener('input', function() {
            // Очищаем предыдущий таймер
            clearTimeout(timeout);

            // Устанавливаем таймер на 500 мс
            timeout = setTimeout(function() {
                if (!slugInput.value) {  // Генерация только если slug еще не введен вручную
                    slugInput.value = slugify(titleInput.value);
                }
            }, 500);  // Задержка 500 мс
        });

        // Сброс slug при редактировании вручную (при наличии предыдущего значения)
        slugInput.addEventListener('input', function() {
            if (!slugInput.value) {
                slugInput.value = slugify(titleInput.value);
            }
        });
    }
});
