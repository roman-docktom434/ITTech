from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    #Извлечение текста из PDF
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def analyze_website(url: str, requirements: str) -> str:
    #Парсинг и анализ сайта
    response = requests.get(url)
    if response.status_code != 200:
        return "Ошибка при доступе к сайту"

    soup = BeautifulSoup(response.text, "html.parser")

    # Пример анализа (проверка наличия ключевых слов из требований)
    keywords = requirements.split()[:10]  # Берем первые 10 слов из требований
    site_text = soup.get_text()
    matches = [word for word in keywords if word in site_text]

    if matches:
        return f"Сайт соответствует требованиям. Найдено совпадений: {len(matches)}"
    else:
        return "Сайт не соответствует требованиям"
