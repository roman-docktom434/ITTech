document.addEventListener("DOMContentLoaded", function() {

    // Обработка загрузки PDF
    document.getElementById("uploadForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById("pdfFile");

        if (fileInput.files.length > 0) {
            formData.append("file", fileInput.files[0]);

            try {
                const response = await fetch("http://127.0.0.1:8000/upload_pdf/", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                if (result.valid) {
                    document.getElementById("pdfResult").innerHTML = "PDF файл прошел проверку!";
                } else {
                    document.getElementById("pdfResult").innerHTML = "Ошибки в PDF: " + result.errors.join(", ");
                }

            } catch (error) {
                document.getElementById("pdfResult").innerHTML = "Ошибка при загрузке файла.";
                console.error(error);
            }
        }
    });

    // Обработка проверки сайта
    document.getElementById("siteForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const url = document.getElementById("siteUrl").value;

        try {
            const response = await fetch("http://127.0.0.1:8000/check_site/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ url: url })
            });

            const result = await response.json();

            // Проверка полученного результата
            console.log(result);  // Логируем результат для отладки

            if (result.valid) {
                document.getElementById("siteResult").innerHTML = "Сайт прошел проверку!";
            } else {
                document.getElementById("siteResult").innerHTML = "Ошибки на сайте: " + result.errors.join(", ");
            }

        } catch (error) {
            document.getElementById("siteResult").innerHTML = "Ошибка при проверке сайта.";
            console.error(error);
        }
    });

});
