const API_BASE_URL = "http://127.0.0.1:8000"; // Убедитесь, что бэк работает на этом адресе

// Элементы DOM
const uploadForm = document.getElementById("upload-form");
const checkForm = document.getElementById("check-form");
const getReportsButton = document.getElementById("get-reports");
const uploadResult = document.getElementById("upload-result");
const checkResult = document.getElementById("check-result");
const reportsList = document.getElementById("reports-list");

// Загрузка файла
uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fileInput = document.getElementById("file");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/upload-requirements/`, {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        uploadResult.innerText = result.message || "Ошибка загрузки файла";
    } catch (error) {
        uploadResult.innerText = "Ошибка соединения с сервером";
    }
});

// Проверка сайта
checkForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const urlInput = document.getElementById("url");

    try {
        const response = await fetch(`${API_BASE_URL}/check-site/`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ url: urlInput.value }),
        });
        const result = await response.json();
        checkResult.innerText = result.result || "Результат проверки неизвестен";
    } catch (error) {
        checkResult.innerText = "Ошибка соединения с сервером";
    }
});

// Получение отчётов
getReportsButton.addEventListener("click", async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/`);
        const reports = await response.json();
        if (Array.isArray(reports)) {
            reportsList.innerHTML = reports
                .map((report) => `<p>${report.url}: ${report.result}</p>`)
                .join("");
        } else {
            reportsList.innerText = reports.message || "Нет доступных отчётов";
        }
    } catch (error) {
        reportsList.innerText = "Ошибка получения отчётов";
    }
});
