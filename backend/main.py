from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import uuid
import os
from utils import extract_text_from_pdf, analyze_website

app = FastAPI()

# Память для хранения данных
uploaded_requirements: Dict[str, str] = {}  # {file_id: текст требований}
last_report: Dict[str, str] = {}  # Последний отчет {url: отчет}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-requirements/")
async def upload_requirements(file: UploadFile):
    #Загрузка и извлечение текста из PDF с требованиями
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Только PDF-файлы поддерживаются")

    # Генерация уникального ID и сохранение файла
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Извлечение текста из PDF
    try:
        extracted_text = extract_text_from_pdf(file_path)
        uploaded_requirements[file_id] = extracted_text
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка обработки PDF")

    return {"message": "Файл успешно загружен", "file_id": file_id}

@app.post("/analyze-site/")
async def analyze_site(url: str = Form(...)):
    #Анализ структуры и контента сайта по требованиям
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL должен начинаться с http:// или https://")

    if not uploaded_requirements:
        raise HTTPException(status_code=400, detail="Сначала загрузите требования")

    # Берем последние загруженные требования
    latest_requirements = list(uploaded_requirements.values())[-1]

    # Анализ сайта
    try:
        result = analyze_website(url, latest_requirements)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка анализа сайта")

    # Сохраняем отчет
    global last_report
    last_report = {"url": url, "result": result}
    return {"url": url, "result": result}

@app.get("/get-report/")
async def get_report():
    #Возвращает последний отчет
    if not last_report:
        return {"message": "Пока нет отчетов"}
    return last_report
