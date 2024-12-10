from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict
import uuid
import os

app = FastAPI()

# Память для хранения данных
uploaded_files: Dict[str, str] = {}  # {file_id: file_path}
site_checks: List[Dict[str, str]] = []  # [{"url": str, "result": str}]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-requirements/")
async def upload_requirements(file: UploadFile):
    #Загрузка PDF-файла.
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Только PDF-файлы поддерживаются")

    # Генерация уникального ID для файла
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    uploaded_files[file_id] = file_path
    return {"message": "Файл успешно загружен", "file_id": file_id}


@app.get("/download-requirements/{file_id}")
async def download_requirements(file_id: str):
    #Скачивание ранее загруженного файла.
    file_path = uploaded_files.get(file_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))


@app.post("/check-site/")
async def check_site(url: str = Form(...)):
    #Проверка сайта.
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL должен начинаться с http:// или https://")

    # Пример простой проверки (можно заменить на реальную логику)
    passed = "https" in url
    result = "Сайт соответствует требованиям" if passed else "Сайт не соответствует требованиям"

    # Сохранение результата в памяти
    site_checks.append({"url": url, "result": result})
    return {"url": url, "result": result}


@app.get("/reports/")
async def get_reports():
    #Получение всех отчетов по проверке сайтов.
    if not site_checks:
        return {"message": "Пока нет проверок"}
    return site_checks
