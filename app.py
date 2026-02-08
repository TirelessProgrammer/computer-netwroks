import os
from flask import Flask, request, send_file, render_template_string
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
# Ensure this file exists in your folder!
FONT_PATH = "DejaVuSans.ttf"

# --- DATA ---
LAB_INFO = {
    "title": "Лабораторна робота №1",
    "description": [
        "Встановлення віртуальної машини згідно схеми загальної архітектури обчислювальних систем в програмах: VirtualPC, Hyper-V, Parallels Desktop (за можливістю), VMWare (за можливістю), Proxmox.",
        "Встановлення програм тестування конфігурації PC.",
        "Обробка параметру device ID.",
        "Надіслати таблицю ID пристроїв доступного обладнання.",
    ],
    "links": [
        {"text": "Створення віртуальної машини за допомогою Hyper-V",
         "url": "https://learn.microsoft.com/uk-ua/virtualization/hyper-v-on-windows/quick-start/create-virtual-machine"},
        {"text": "Завантаження Windows 10", "url": "https://www.microsoft.com/uk-ua/software-download/windows10"},
        {"text": "Завантаження VirtualBox", "url": "https://www.virtualbox.org/wiki/Downloads"},
    ],
    "steps": [
        {
            "id": "step1",
            "title": "Крок 1. Аналіз ресурсів",
            "content": "Аналіз робочого ПК та планування розподілу пам'яті та обчислювальних ресурсів для встановлення 2-х віртуальних машин Windows, FreeBSD.",
            "type": "text"
        },
        {
            "id": "step2",
            "title": "Крок 2. Вибір гіпервізору",
            "content": "Вибір типу гіпервізору, в залежності від типу базової ОС ПК: VirtualPC, Hyper-V, Parallels Desktop (за можливістю), VMWare (за можливістю), Proxmox, VirtualBox (Win, Mac, Linux). (Огляд - таблиця найбільш популярних гіпервізорів з вікіпедії).",
            "type": "text"
        },
        {
            "id": "step3",
            "title": "Крок 3. Встановлення гіпервізору",
            "content": "Встановити вибраний гіпервізор.",
            "task": "Вказати який вибрано, обгрунтувати вибір.",
            "type": "input"
        },
        {
            "id": "step4",
            "title": "Крок 4. Налаштування Windows",
            "content": """Встановлення віртуальних машин у вибраних програмах гіпервізору:

    для Windows вибирайте розмір VHDX від 15 Гб, ОЗП від 2048 Мб.
    В назві жорсткого диску та віртуальної машини потрібно вказати прізвище та номер групи, наприклад Shevchenko_K14.vhdx.

    Систему, що встановлюється, налаштовуйте для “особистого використовування”, при встановлюванні системи вибирайте найпростіші ідентифікатори та записуйте їх.
    В налаштуваннях конфіденційності завжди відповідайте - Ні.
    Пропускайте ті поля, які дозволяють Вам пройти далі без заповнення.""",
            "type": "text"
        },
        {
            "id": "step5",
            "title": "Крок 5. Налаштування FreeBSD",
            "content": """для Freebsd VHDX від 25 Гб, ОЗП від 4096 Мб.
    Детальніше: https://docs.freebsd.org/en/books/handbook/bsdinstall/""",
            "type": "text"
        },
        {
            "id": "step6",
            "title": "Крок 6. Аналіз комплектації",
            "content": "Оглядовий аналіз комплектації віртуальної ОС згідно схеми загальної архітектури обчислювальних систем.",
            "task": "Зробити оглядовий аналіз комплектації (текст/скріншоти).",
            "type": "input"
        },
        {
            "id": "step7",
            "title": "Крок 7. Тестування та Device ID",
            "content": "Встановлення програм тестування конфігурації PC (напр., Everest). Обробка параметру device ID.",
            "task": "Надіслати таблицю ID пристроїв доступного обладнання із вказанням назви та призначенням відповідної компоненти.",
            "type": "input"
        }
    ]
}

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>{{ lab.title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #fdfdfd; color: #333; }
        h1 { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
        h2 { color: #0056b3; margin-top: 30px; border-left: 5px solid #0056b3; padding-left: 10px; }
        .section { background: #fff; padding: 15px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .step-card { background: #f8f9fa; margin-bottom: 25px; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; }
        .step-title { font-size: 1.2em; font-weight: bold; color: #495057; margin-bottom: 10px; }
        .input-area { margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ccc; }
        .file-wrapper { margin-top: 5px; }
        .add-file-btn { background: #6c757d; color: white; border: none; padding: 5px 10px; font-size: 0.9em; border-radius: 3px; cursor: pointer; margin-top: 10px; }
        .add-file-btn:hover { background: #5a6268; }

        .submit-btn { display: block; width: 100%; padding: 15px; background: #28a745; color: white; border: none; font-size: 1.2em; cursor: pointer; border-radius: 5px; margin-top: 30px; }
        .submit-btn:hover { background: #218838; }
    </style>
    <script>
        // JavaScript to add new file inputs dynamically
        function addFileInput(stepId) {
            var container = document.getElementById("file-container-" + stepId);
            var div = document.createElement("div");
            div.className = "file-wrapper";
            
            var input = document.createElement("input");
            input.type = "file";
            input.name = "files_" + stepId; // Use SAME name for all inputs in this step
            input.accept = "image/*";
            
            div.appendChild(input);
            container.appendChild(div);
        }
    </script>
</head>
<body>
    <h1>{{ lab.title }}</h1>
    <form action="/generate" method="post" enctype="multipart/form-data">
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
            <h3>Дані студента</h3>
            <label>Прізвище та Ім'я:</label>
            <input type="text" name="student_name" placeholder="Іванов Іван" style="width: 100%; padding: 8px; margin-bottom: 10px;">
            <label>Група:</label>
            <input type="text" name="group_code" placeholder="К-14" style="width: 100%; padding: 8px;">
        </div>

        <h2>Опис лабораторної</h2>
        <div class="section">
            <ul>
            {% for item in lab.description %}
                <li>{{ item }}</li>
            {% endfor %}
            </ul>
        </div>

        <h2>Корисні посилання</h2>
        <div class="section">
            <ul>
            {% for link in lab.links %}
                <li><a href="{{ link.url }}" target="_blank">{{ link.text }}</a></li>
            {% endfor %}
            </ul>
        </div>

        <h2>Порядок виконання</h2>
        {% for step in lab.steps %}
        <div class="step-card">
            <div class="step-title">{{ step.title }}</div>
            <div style="white-space: pre-wrap;">{{ step.content }}</div>
            {% if step.type == 'input' %}
            <div class="input-area">
                <p><strong>Завдання до звіту:</strong> {{ step.task }}</p>
                
                <label>Ваш текст:</label>
                <textarea name="text_{{ step.id }}" rows="3"></textarea>
                
                <p style="margin-bottom: 5px; font-weight: bold;">Скріншоти:</p>
                
                <div id="file-container-{{ step.id }}">
                    <div class="file-wrapper">
                        <input type="file" name="files_{{ step.id }}" accept="image/*">
                    </div>
                </div>
                
                <button type="button" class="add-file-btn" onclick="addFileInput('{{ step.id }}')">+ Додати ще скріншот</button>
            </div>
            {% endif %}
        </div>
        {% endfor %}

        <button type="submit" class="submit-btn">Згенерувати PDF-звіт</button>
    </form>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, lab=LAB_INFO)


@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        if not os.path.exists(FONT_PATH):
            return "Error: Font file missing.", 500

        pdf = FPDF()
        pdf.add_page()

        # Fonts
        pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
        pdf.add_font('DejaVu', 'B', FONT_PATH, uni=True)
        pdf.set_font("DejaVu", size=11)

        def print_text(text, is_bold=False, size=11):
            pdf.set_font("DejaVu", style='B' if is_bold else '', size=size)
            pdf.set_x(10)
            pdf.multi_cell(190, 6, text)

        s_name = request.form.get('student_name', 'Не вказано')
        s_group = request.form.get('group_code', 'Не вказано')

        # Header
        pdf.set_font("DejaVu", 'B', 16)
        pdf.cell(0, 10, LAB_INFO['title'], ln=True, align='C')
        pdf.set_font("DejaVu", '', 10)
        pdf.cell(0, 6, f"Студент: {s_name} | Група: {s_group}", ln=True, align='C')
        pdf.cell(0, 6, f"Дата: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
        pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
        pdf.ln(10)

        # Description
        print_text("Опис та вимоги:", is_bold=True, size=12)
        pdf.ln(2)
        for item in LAB_INFO['description']:
            print_text(f"- {item}", size=10)
        pdf.ln(5)

        # Steps Loop
        print_text("Хід виконання роботи:", is_bold=True, size=12)
        pdf.ln(5)

        for step in LAB_INFO['steps']:
            # Step Title
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("DejaVu", 'B', 11)
            pdf.set_x(10)
            pdf.cell(190, 8, step['title'], ln=True, fill=True)

            # Step Content
            pdf.ln(2)
            print_text(step['content'], size=10)
            pdf.ln(2)

            # If Input Step
            if step['type'] == 'input':
                # Task Description
                print_text(f"Завдання: {step['task']}", is_bold=True, size=10)
                pdf.ln(2)

                # User Answer
                user_text = request.form.get(f"text_{step['id']}", "")
                # getlist grabs ALL files from ALL inputs with this name
                user_files = request.files.getlist(f"files_{step['id']}")

                if user_text.strip():
                    print_text(f"Відповідь: {user_text}", size=10)
                    pdf.ln(2)

                # Images
                for f in user_files:
                    if f and f.filename:
                        temp_path = f"/tmp/{f.filename}"
                        f.save(temp_path)
                        try:
                            # Add page if needed
                            if pdf.get_y() > 220:
                                pdf.add_page()

                            pdf.set_x(15)
                            pdf.image(temp_path, w=160)
                            pdf.ln(5)
                        except Exception as e:
                            print(f"Image error: {e}")
            pdf.ln(5)

        pdf_out = "/tmp/Report.pdf"
        pdf.output(pdf_out)
        return send_file(pdf_out, as_attachment=True, download_name=f"Report_Lab1.pdf")

    except Exception as e:
        return f"System Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
