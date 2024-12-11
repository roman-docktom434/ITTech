from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
import PyPDF2
import requests
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Разрешаем CORS для всех доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных для запросов и ответов
class CheckSiteResponse(BaseModel):
    result: str
    score: int
    issues: list

class Report(BaseModel):
    url: str
    result: str
    score: int
    issues: list

# Статус сервера
@app.get("/status/")
async def get_status():
    return {"status": "Server is running"}

# Загружаем PDF и извлекаем требования
def extract_requirements_from_pdf(file_content):
    try:
        pdf_reader = PyPDF2.PdfReader(file_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # Здесь можно обработать текст для извлечения конкретных требований
        return text.split("\n")  # Возвращаем требования построчно
    except Exception as e:
        logging.error(f"Ошибка при обработке PDF: {str(e)}")
        return []

# Проверка сайта на основе извлеченных требований
def check_site_against_requirements(url, requirements):
    issues = []
    satisfied_count = 0  # Считаем удовлетворенные требования
    total_requirements = len(requirements)  # Общее количество требований
    
    # Пример проверки сайта по требованию (можно расширить)
    response = requests.get(url)
    if response.status_code != 200:
        issues.append(f"Сайт {url} недоступен.")
    else:
        for requirement in requirements:
            if requirement.lower() in response.text.lower():
                satisfied_count += 1  # Удовлетворено требование
            else:
                issues.append(f"Не найдено требование: {requirement}")

    score = (satisfied_count / total_requirements) * 10 if total_requirements > 0 else 0  # Оценка из 10 на основе удовлетворенных требований
    return issues, satisfied_count, total_requirements, score

# Загружаем файл PDF
@app.post("/upload-requirements/")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logging.info(f"Файл {file.filename} успешно загружен.")
        return {"message": f"Файл {file.filename} успешно загружен", "filename": file.filename}
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

# Проверка сайта
@app.post("/check-site/")
async def check_site(url: str = Form(...), pdf_filename: str = Form(...)):
    try:
        # Чтение PDF с требованиями
        pdf_path = os.path.join("uploads", pdf_filename)
        with open(pdf_path, "rb") as f:
            requirements = extract_requirements_from_pdf(f)
        
        if not requirements:
            raise HTTPException(status_code=400, detail="Требования не найдены в PDF")

        # Проверка сайта
        issues, satisfied_count, total_requirements, score = check_site_against_requirements(url, requirements)

        # Формирование результата
        if satisfied_count == total_requirements:
            result = "Сайт соответствует всем требованиям."
        else:
            result = f"Сайт не соответствует всем требованиям. Удовлетворено требований {satisfied_count}/{total_requirements}"

        return CheckSiteResponse(
            result=result,
            score=int(score),
            issues=issues
        )

    except Exception as e:
        logging.error(f"Ошибка при проверке сайта: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при проверке: {str(e)}")

# Формирование отчёта
@app.post("/generate-report/") 
async def generate_report(url: str = Form(...), pdf_filename: str = Form(...)):
    try:
        # Чтение PDF с требованиями
        pdf_path = os.path.join("uploads", pdf_filename)
        with open(pdf_path, "rb") as f:
            requirements = extract_requirements_from_pdf(f)

        if not requirements:
            raise HTTPException(status_code=400, detail="Требования не найдены в PDF")

        # Проверка сайта
        issues, satisfied_count, total_requirements, score = check_site_against_requirements(url, requirements)

        report = {
            "url": url,
            "result": "Соответствует" if not issues else "Не соответствует",
            "score": score,
            "issues": issues,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        report_filename = f"report_{url.replace('http://', '').replace('https://', '').replace('/', '_')}.txt"
        report_path = os.path.join("reports", report_filename)
        os.makedirs("reports", exist_ok=True)

        with open(report_path, "w") as f:
            f.write(f"URL: {url}\n")
            f.write(f"Результат: {report['result']}\n")
            f.write(f"Оценка: {report['score']} / 10\n")
            f.write(f"Проблемы:\n")
            for issue in report['issues']:
                f.write(f"- {issue}\n")
            f.write(f"\nВремя создания отчета: {report['timestamp']}")

        return JSONResponse(content={"message": "Отчёт сформирован", "report_url": f"/reports/{report_filename}"})
    except Exception as e:
        logging.error(f"Ошибка при формировании отчёта: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при формировании отчёта: {str(e)}")
