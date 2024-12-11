from pathlib import Path
import pdfplumber
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Настроим CORS для разрешения запросов с фронтенда
app = FastAPI()

# Разрешаем доступ с домена 127.0.0.1:5500 (или можете разрешить все домены с '*')
origins = [
    "http://127.0.0.1:5500",  # Фронтенд-сервер
    "http://localhost:5500",  # Можно добавить локальный сервер
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешаем доступ только с этих доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Модели для валидации данных
class SiteRequest(BaseModel):
    url: str

# utils.py (для обработки файлов и других утилит)
def allowed_file(filename: str) -> bool:
    """
    Проверяет, является ли файл допустимым для загрузки.
    Разрешены только PDF файлы.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# Логика проверки требований
def check_site_requirements(site_url: str) -> dict:
    """
    Проверяет сайт на соответствие требованиям.
    Это будет заглушка для реальной проверки сайта.
    """
    site_data = {
        "valid": True,
        "errors": []
    }

    # Пример проверки: проверка наличия определённого контента на сайте
    if "example.com" not in site_url:
        site_data["valid"] = False
        site_data["errors"].append("Сайт не соответствует требованиям.")

    return site_data

# Логика обработки и проверки PDF
def process_pdf_and_check_site(pdf_path: str) -> dict:
    """
    Обрабатывает PDF файл и проверяет его содержимое на соответствие
    правилам для образовательных сайтов.
    """
    site_data = {
        "valid": True,
        "errors": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

        # Пример проверки: проверка наличия ключевых слов
        if "образование" not in text:
            site_data["valid"] = False
            site_data["errors"].append("Отсутствует ключевое слово 'образование'.")

    return site_data

# Функция для загрузки требований
def upload_requirements(file: UploadFile) -> dict:
    """
    Загружает файл с требованиями для сайта и проверяет его содержание.
    """
    if file and allowed_file(file.filename):
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        
        result = process_pdf_and_check_site(file_location)
        return result

    return {"message": "Недопустимый формат файла"}

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Обрабатывает загруженный PDF файл и проверяет его на соответствие.
    """
    result = upload_requirements(file)
    return JSONResponse(content=result)

@app.post("/check_site/")
async def check_site(data: SiteRequest):
    """
    Проверяет сайт на соответствие требованиям.
    """
    result = check_site_requirements(data.url)
    return JSONResponse(content=result)

@app.get("/status/")
async def get_status():
    """
    Получить статус сервера.
    """
    return {"status": "running", "version": "1.0.0"}

# Настройка директории для хранения файлов
uploads_dir = Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

# Основная точка входа
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
