import socket
from urllib.parse import parse_qs, unquote

HOST = 'localhost'
PORT = 8080

# Словарь для хранения оценок
grades = {}

def build_html():
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Журнал оценок</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                max-width: 600px;
                width: 90%;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-weight: 500;
                font-size: 2.5em;
            }
            h2 {
                color: #555;
                margin-top: 30px;
                margin-bottom: 20px;
                font-weight: 400;
            }
            form {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 15px;
                font-weight: 500;
                color: #333;
                text-align: left;
            }
            input {
                width: 100%;
                padding: 12px;
                margin-top: 5px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
                font-weight: 500;
            }
            button:hover {
                transform: translateY(-2px);
            }
            hr {
                border: none;
                height: 2px;
                background: linear-gradient(90deg, transparent, #667eea, transparent);
                margin: 30px 0;
            }
            .grade-item {
                background: #f8f9fa;
                margin: 15px 0;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                text-align: left;
            }
            .no-grades {
                color: #666;
                font-style: italic;
                margin: 30px 0;
            }
            .subject-name {
                color: #333;
                font-weight: 500;
                margin-bottom: 5px;
            }
            .grades-list {
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Журнал оценок</h1>
            <form method="POST" action="/">
                <label>Дисциплина: 
                    <input name="discipline" placeholder="Введите название дисциплины" required>
                </label>
                <label>Оценка: 
                    <input name="grade" type="number" min="2" max="5" placeholder="Введите оценку от 2 до 5" required>
                </label>
                <button type="submit">📝 Добавить оценку</button>
            </form>
            <hr>
            <h2>Список оценок</h2>
    """
    # добавление оценок
    if grades:
        # название предмета и оценка
        for subject, marks in grades.items():
            html += f"<p><b>{subject}</b>: {', '.join(map(str, marks))}</p>"
    else:
        html += "<p>Пока нет оценок</p>"

    html += """
    </body>
    </html>
    """
    return html


def handle_client(client_socket):
    request = client_socket.recv(4096).decode('utf-8', errors="ignore")
    # разделение заголовка и тела запроса
    headers, _, body = request.partition('\r\n\r\n')
    header_lines = headers.split("\r\n")
    first_line = headers.splitlines()[0]
    method = first_line.split()[0]

    # обработка post запроса - добавление новой оценки
    if method == "POST":
        content_length = 0
        # поиск заголовка
        for line in header_lines:
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())
        # дополнительный запрос тела, если оно пришло не полностью
        while len(body.encode("utf-8")) < content_length:
            body += client_socket.recv(4096).decode("utf-8", errors="ignore")

        # парсинг даных
        parsed = parse_qs(body)
        subject = unquote(parsed.get("discipline", ["Без названия"])[0])
        grade = parsed.get("grade", [None])[0]

        # добавление оценки в словарь
        if grade:
            try:
                grade = int(grade)
                grades.setdefault(subject, []).append(grade)
            except ValueError:
                pass
    # билд html страницы
    html = build_html()
    # формирование http ответа
    response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(html.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
            + html
    )
    client_socket.sendall(response.encode("utf-8"))
    client_socket.close()


def func_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        # принимаем соединения и обрабатываем запросы
        client_socket, addr = server.accept()
        handle_client(client_socket)

func_server()
