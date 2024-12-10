# main.py
from fastapi import FastAPI, UploadFile, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
import pdfplumber
import requests

# Инициализация приложения и базы данных
app = FastAPI()
DATABASE_URL = "postgresql://user:password@localhost/ai_auditor"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модели базы данных
class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

class SiteCheck(Base):
    __tablename__ = "site_checks"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    report = Column(Text, nullable=False)
    passed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Функции для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для загрузки требований из PDF
@app.post("/upload-requirements/")
async def upload_requirements(file: UploadFile, db=next(get_db())):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Требуется PDF файл")
    
    try:
        with pdfplumber.open(file.file) as pdf:
            content = "\n".join([page.extract_text() for page in pdf.pages])
        db.add(Requirement(content=content))
        db.commit()
        return {"message": "Требования успешно загружены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Маршрут для проверки сайта
@app.post("/check-site/")
async def check_site(url: str, db=next(get_db())):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Сайт недоступен")
        
        soup = BeautifulSoup(response.text, "html.parser")
        site_content = soup.get_text()

        requirements = db.query(Requirement).all()
        violations = []
        for req in requirements:
            if req.content not in site_content:
                violations.append(req.content)

        passed = len(violations) == 0
        report = f"Проверено: {url}\nСоответствий: {'Все требования соблюдены' if passed else 'Найдены несоответствия'}"
        db.add(SiteCheck(url=url, report=report, passed=passed))
        db.commit()
        return {"url": url, "passed": passed, "violations": violations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Маршрут для получения отчетов
@app.get("/reports/")
async def get_reports(db=next(get_db())):
    reports = db.query(SiteCheck).all()
    return [{"url": r.url, "report": r.report, "passed": r.passed} for r in reports]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
