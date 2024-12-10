const uploadForm = document.getElementById("upload-form");
const checkForm = document.getElementById("check-form");
const getReportsButton = document.getElementById("get-reports");

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fileInput = document.getElementById("file");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("http://localhost:8000/upload-requirements/", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        document.getElementById("upload-result").innerText = result.message || "Ошибка загрузки";
    } catch (error) {
        document.getElementById("upload-result").innerText = "Ошибка соединения с сервером";
    }
});

checkForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const urlInput = document.getElementById("url");

    try {
        const response = await fetch("http://localhost:8000/check-site/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: urlInput.value }),
        });
        const result = await response.json();
        const checkResult = result.passed
            ? "Сайт соответствует всем требованиям"
            : `Найдены несоответствия: ${result.violations.join(", ")}`;
        document.getElementById("check-result").innerText = checkResult;
    } catch (error) {
        document.getElementById("check-result").innerText = "Ошибка соединения с сервером";
    }
});

getReportsButton.addEventListener("click", async () => {
    try {
        const response = await fetch("http://localhost:8000/reports/");
        const reports = await response.json();
        const reportsList = document.getElementById("reports-list");
        reportsList.innerHTML = reports
            .map((report) => `<p>${report.url}: ${report.report}</p>`)
            .join("");
    } catch (error) {
        document.getElementById("reports-list").innerText = "Ошибка получения отчётов";
    }
});
