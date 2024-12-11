url = input('Введите ссылку на сайт учебного заведения: ')
if not url.startswith('http'):
    while not url.startswith('http'):
        url = input('Введите ссылку на сайт учебного заведения: ')
sveden_list = ['common', 'struct', 'document', 'education', 'eduStandarts', 'managers', 'employees', 'object', 'grants', 'paid_edu', 'budget', 'vacant', 'inter', 'catering']
clear_list = []
ru_url = url.find('ru')
for sveden in sveden_list:
    clear_list.append(url[:ru_url+2] + f'/sveden/{sveden}')
import PyPDF2

# Открываем PDF-файл для чтения в бинарном режиме
pdf_file = open('metodicheskie-rekomendaczii-2024 (1).pdf', 'rb')

# Создаем объект PdfReader
pdf_reader = PyPDF2.PdfReader(pdf_file)
f_text = []
# Получаем количество страниц в PDF
num_pages = len(pdf_reader.pages)
text_from_pdf = []
rating = []
# Проходим по каждой странице и выводим текст
for page in range(num_pages):
    pdf_page = pdf_reader.pages[page]
    text_from_pdf.append(pdf_page.extract_text())
pdf_file.close()
metodichka = '\n'.join(text_from_pdf)
for site in clear_list:
    r = requests.get(site)
    maw = BeautifulSoup(r.text).text
    if len(maw) > 3000000:
        None
    else:
        prompt = '(1)' + metodichka + '\n' + 'Ты опытный оценщик. Первый (1) текст перед тобой это "Методические рекомендации представления информации об образовательной организации в открытых источниках с учетом соблюдения требований законодательства в сфере образования", второй (2) текст это сам сайт. Дай оценку по десятибальной (0, 10) оценку сайту. Оценка должна учитывать только то, как создан сайт. В ответе должна быть ТОЛЬКО оценка. Пример: 7 из 10.' + '\n' + '(2)' + maw
        def get_answer(text):
            i = 0
            while i < 10:
                client = G4FClient()
                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages=[{"role": "user", "content": text}],
                )
                res = response.choices[0].message.content
                i += 1

                if len(res) > 0 and 'Model' not in res and 'error' not in res and 'chat' not in res:
                    return res
                    break
    rating.append(get_answer(prompt))
total = 0
for t in rating:
    mark = int(t.split('из')[0])
    total += mark
print(round(total/14, 1))
