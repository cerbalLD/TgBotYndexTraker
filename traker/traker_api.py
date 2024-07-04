from flask import Flask, request, jsonify
import requests
import json
import os

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

# Определение пути к config.json
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

# Загрузка конфигурации
config = load_config(config_path)

# Извлечение нужных значений из config
tracker_host = config['tracker_host']
tracker_port = config['tracker_port']
bot_host_all = config['bot_host_all']

app = Flask(__name__)

@app.route('/tracker/settings', methods=['POST'])
def handle_tracker_create_task():
    try:
        data = request.get_json()

        comment_text = data.get('comment_text')

        lines = comment_text.splitlines()
        [line for line in lines if line != '']

        phone = lines[0]
        phone = phone.replace("\\+",'')
        date = lines[3]

        # URL вашего сервера Flask
        url = bot_host_all+'/settings'

        # Данные для отправки
        data = {
            "phone": phone,
            "date": date
        }

        # Преобразование данных в JSON формат
        payload = json.dumps(data)

        # Заголовки HTTP запроса
        headers = {
            'Content-Type': 'application/json'
        }

        # Отправка POST запроса
        response = requests.post(url, headers=headers, data=payload)

        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tracker/create_task', methods=['POST'])
def handle_tracker_settings():
    try:
        data = request.get_json()

        task_id = data.get('issue_id')
        comment_text = data.get('comment_text')

        lines = comment_text.splitlines()
        [line for line in lines if line != '']

        phone = lines[0]
        phone = phone.replace("\\+",'')
        task_name = lines[1]
        text = lines[2]
        date = lines[3]
        documents_names = lines[4].split(',')
        documents = [{"name": document_name} for document_name in documents_names]

        # URL вашего сервера Flask
        url = bot_host_all+'/create_task'

        # Данные для отправки
        data = {
            "phone": phone,
            "task_name": task_name,
            "task_id": task_id,
            "message_text": text,
            "documents": documents
        }

        # Преобразование данных в JSON формат
        payload = json.dumps(data)

        # Заголовки HTTP запроса
        headers = {
            'Content-Type': 'application/json'
        }

        # Отправка POST запроса
        response = requests.post(url, headers=headers, data=payload)

        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tracker/mailing/status', methods=['POST'])
def handle_tracker_mailing_status():
    try:
        data = request.get_json()

        task_id = data.get('issue_id')
        comment_text = data.get('comment_text')

        lines = comment_text.splitlines()
        [line for line in lines if line != '']

        phone = lines[0]
        task_name = lines[1]
        status = lines[2]
        if status == 'start':
            status = False
        elif status == 'stop':
            status = True
        else:
            return 'error'

        # URL вашего сервера Flask
        url = bot_host_all+'/mailing/status'

        # Данные для отправки
        data = {
            "phone": phone,
            "task_name": task_name,
            "task_id": task_id,
            "status": status
        }

        # Преобразование данных в JSON формат
        payload = json.dumps(data)

        # Заголовки HTTP запроса
        headers = {
            'Content-Type': 'application/json'
        }

        # Отправка POST запроса
        response = requests.post(url, headers=headers, data=payload)

        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tracker/document/status', methods=['POST'])
def handle_tracker_document_status():
    try:
        data = request.get_json()

        task_id = data.get('issue_id')
        comment_text = data.get('comment_text')

        lines = comment_text.splitlines()
        [line for line in lines if line != '']

        phone = lines[0]
        task_name = lines[1]
        name = lines[2]
        status = lines[3]
        if status == 'start':
            status = False
        elif status == 'stop':
            status = True
        else:
            return 'error'

        # URL вашего сервера Flask
        url = bot_host_all+'/document/status'

        # Данные для отправки
        data = {
            "phone": phone,
            "name": name,
            "task_name": task_name,
            "task_id": task_id,
            "status": status
        }

        # Преобразование данных в JSON формат
        payload = json.dumps(data)

        # Заголовки HTTP запроса
        headers = {
            'Content-Type': 'application/json'
        }

        # Отправка POST запроса
        response = requests.post(url, headers=headers, data=payload)

        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tracker/document/add', methods=['POST'])
def handle_tracker_document_add():
    try:
        data = request.get_json()

        task_id = data.get('issue_id')
        comment_text = data.get('comment_text')

        lines = comment_text.splitlines()
        [line for line in lines if line != '']

        phone = lines[0]
        task_name = lines[1]
        name = lines[2]

        # URL вашего сервера Flask
        url = bot_host_all+'/document/add'

        # Данные для отправки
        data = {
            "phone": phone,
            "task_name": task_name,
            "task_id": task_id,
            "name": name
        }

        # Преобразование данных в JSON формат
        payload = json.dumps(data)

        # Заголовки HTTP запроса
        headers = {
            'Content-Type': 'application/json'
        }

        # Отправка POST запроса
        response = requests.post(url, headers=headers, data=payload)

        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# работа с api яндекс трекера
yandex_tracker_api_url = config['yandex_tracker_api_url']
yandex_tracker_oauth_token = config['yandex_tracker_oauth_token']
yandex_tracker_org_id = config['yandex_tracker_org_id']

# Функция для загрузки файла в Яндекс.Трекер
def upload_file_to_task(issue_id, file_path):
    url = f"{yandex_tracker_api_url}/issues/{issue_id}/attachments"
    headers = {
        "Authorization": f"OAuth {yandex_tracker_oauth_token}",
        "X-Org-ID": yandex_tracker_org_id
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response

# Функция для добавления комментария к задаче в Яндекс.Трекер
def add_comment_to_task(issue_id, comment_text):
    url = f"{yandex_tracker_api_url}/issues/{issue_id}/comments"
    headers = {
        "Authorization": f"OAuth {yandex_tracker_oauth_token}",
        "X-Org-ID": yandex_tracker_org_id,
        "Content-Type": "application/json"
    }
    data = {"text": comment_text}
    response = requests.post(url, headers=headers, json=data)
    return response

@app.route('/tracker/upload_file', methods=['POST'])
def handle_upload_file():
    data = request.get_json()
    issue_id = data.get('issue_id')
    file_path = data.get('file_path')  # Предполагаем, что путь к файлу передается в запросе

    # Загрузка файла
    upload_response = upload_file_to_task(issue_id, file_path)
    if upload_response.status_code != 200:
        return jsonify({'error': 'Failed to upload file', 'details': upload_response.json()}), upload_response.status_code

    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/tracker/add_comment', methods=['POST'])
def handle_add_comment():
    data = request.get_json()
    issue_id = data.get('issue_id')
    comment_text = data.get('comment_text')

    # Добавление комментария
    comment_response = add_comment_to_task(issue_id, comment_text)
    if comment_response.status_code != 201:
        return jsonify({'error': 'Failed to add comment', 'details': comment_response.json()}), comment_response.status_code

    return jsonify({'message': 'Comment added successfully'}), 200

def start_traker_api():
    app.run(host=tracker_host, port=tracker_port)

# Запуск приложения
if __name__ == '__main__':
    start_traker_api()