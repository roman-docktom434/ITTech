// Получаем элементы для работы
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file');
const uploadResult = document.getElementById('upload-result');

const checkForm = document.getElementById('check-form');
const urlInput = document.getElementById('url');
const checkResult = document.getElementById('check-result');

const getReportsButton = document.getElementById('get-reports');
const reportsList = document.getElementById('reports-list');

// Обработчик загрузки файла
uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        uploadResult.textContent = 'Пожалуйста, выберите файл.';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        uploadResult.textContent = 'Загрузка файла...';

        const response = await fetch('http://127.0.0.1:8000/upload-requirements/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки файла');
        }

        const result = await response.json();
        uploadResult.innerHTML = `PDF успешно загружен: ${result.filename}`;
    } catch (error) {
        uploadResult.textContent = `Ошибка: ${error.message}`;
    }
});

// Обработчик проверки сайта
checkForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const url = urlInput.value;
    const file = fileInput.files[0];

    if (!url || !file) {
        checkResult.textContent = 'Пожалуйста, загрузите файл и введите URL.';
        return;
    }

    checkResult.textContent = 'Проверка сайта...';

    try {
        const formData = new FormData();
        formData.append('url', url);
        formData.append('pdf_filename', file.name);

        const response = await fetch('http://127.0.0.1:8000/check-site/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Ошибка проверки сайта');
        }

        const result = await response.json();
        const { totalRequirements, matchedRequirements } = result;

        // Упрощенный вывод
        checkResult.innerHTML = `
            Результат: Удовлетворено требований ${matchedRequirements}/${totalRequirements}
        `;
    } catch (error) {
        checkResult.textContent = `Ошибка: ${error.message}`;
    }
});

// Получение отчётов
getReportsButton.addEventListener('click', async () => {
    try {
        reportsList.innerHTML = 'Загрузка отчётов...';

        const response = await fetch('http://127.0.0.1:8000/reports/');
        if (!response.ok) {
            throw new Error('Ошибка получения отчётов');
        }

        const reports = await response.json();
        if (reports.length === 0) {
            reportsList.textContent = 'Нет доступных отчётов.';
            return;
        }

        reportsList.innerHTML = reports.map(report => `
            <div class="report-item">
                <a href="${report.url}" target="_blank">${report.name}</a>
            </div>
        `).join('');
    } catch (error) {
        reportsList.textContent = `Ошибка: ${error.message}`;
    }
});
