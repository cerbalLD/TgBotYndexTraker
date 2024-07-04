from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from models import engine
from database_operations import (
    add_user, 
    add_mailing, 
    add_document,
    update_user_date, 
    update_document_status_by_task_and_name_and_phone, 
    update_mailing_status_by_task_id_and_phone,
    get_mailings_by_phone_and_task_id,
    get_documents_by_task_and_name_and_phone,
    add_document_to_pending_task,
    get_user_by_phone
)
import json
import os

from bot import handle_send

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

# Определение пути к config.json
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

# Загрузка конфигурации
config = load_config(config_path)

# Извлечение нужных значений из config
bot_host = config['bot_host']
bot_port = config['bot_port']

# Инициализация базы данных SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Инициализация Flask приложения
app = Flask(__name__)

# Маршруты API
# POST
# создание рассылки
@app.route('/create_task', methods=['POST'])
def create_all():
    try:
        data = request.json
        print(f"[create_task] Received data: {data}")
        
        # Создание пользователя или его обновление
        phone = data.get('phone')

        user = get_user_by_phone(phone)
        if user:
            print(f"[create_task] User already exists: {user}")
        else:
            user = add_user(phone)
            print(f"[create_task] Added new user: {user}")
        
        # Создание рассылки
        message_text = data.get('message_text')
        task_name = data.get('task_name')
        task_id = data.get('task_id')
        mailing = add_mailing(user.id, task_name, message_text, task_id)
        print(f"[create_task] Created mailing: {mailing}")
        
        # Создание документов
        documents_data = data.get('documents', [])
        documents = []
        documents_names = ''

        for doc in documents_data:
            name = doc.get('name')

            documents_names += name + ', '

            document = add_document(name, mailing.id)
            documents.append(document)
            print(f"[create_task] Added document: {document}")

        handle_send(f'У вас появилась новая задача по которой нужно отправить документы "{task_name}": {documents_data[:-1]}', phone)
        
        return jsonify({
            'user': {'id': user.id, 'phone': user.phone, 'chat_id': user.chat_id, 'date': user.date},
            'mailing': {'id': mailing.id, 'task_name': mailing.task_name, 'message_text': mailing.message_text, 'status': mailing.status},
            'documents': [{'id': document.id, 'name': document.name, 'status': document.status} for document in documents]
        }), 200
    except Exception as e:
        print(f"[create_task] Exception: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/settings', methods=['POST'])
def settings():
    try:
        data = request.json
        print(f"[settings] Received data: {data}")
        
        # Создание пользователя или его обновление
        phone = data.get('phone')
        date = data.get('date')

        user = get_user_by_phone(phone)
        if user:
            user = update_user_date(phone, date)
            print(f"[settings] Update user date: {user}")
            handle_send(f'Теперь мы будем вам напоминать о необходимости отправить документы в {date} каждый день', phone)
        else:
            user = add_user(phone, None, data)
            print(f"[settings] Added new user: {user}")
        
        return jsonify({
            'user': {'id': user.id, 'phone': user.phone, 'chat_id': user.chat_id, 'date': user.date}
        }), 200
    except Exception as e:
        print(f"[create_task] Exception: {e}")
        return jsonify({'error': str(e)}), 500

#PUT
# изменение статуса рассылки
@app.route('/mailing/status', methods=['POST'])
def update_mailing():
    try:
        data = request.json
        print(f"[update_mailing] Received data: {data}")

        phone = data.get('phone')
        task_name = data.get('task_name')
        task_id = data.get('task_id')
        status = data.get('status')

        mailing = update_mailing_status_by_task_id_and_phone(phone, task_name, task_id, status)
        print(f"[update_mailing] Updated mailing: {mailing}")

        if status:
            handle_send(f'Администратор закрыл задачу "{task_name}"', phone)
        else:
            handle_send(f'Администратор обновил задачу "{task_name}"', phone)

        if mailing:
            return jsonify({'id': mailing.id, 'status': mailing.status}), 200
        else:
            return jsonify({'error': 'Mailing not found'}), 404
    except Exception as e:
        print(f"[update_mailing] Exception: {e}")
        return jsonify({'error': str(e)}), 500

# изменение статуса документа
@app.route('/document/status', methods=['POST'])
def update_document():
    try:
        data = request.json
        print(f"[update_document] Received data: {data}")

        phone = data.get('phone')
        task_name = data.get('task_name')
        task_id = data.get('task_id')
        name = data.get('name')
        status = data.get('status')

        document = update_document_status_by_task_and_name_and_phone(phone, task_id, name, status)
        print(f"[update_document] Updated document: {document}")

        if status:
            handle_send(f'Администратор закрыл докумет "{name}" в задаче "{task_name}"', phone)
        else:
            handle_send(f'Отправьте "{name}" в задаче "{task_name}" еще раз, пожалуйста', phone)

        if document:
            return jsonify({'id': document.id, 'status': document.status}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        print(f"[update_document] Exception: {e}")
        return jsonify({'error': str(e)}), 500

# добавление документа
@app.route('/document/add', methods=['POST'])
def add_document_to_task():
    try:
        data = request.json
        print(f"[add_document_to_task] Received data: {data}")

        phone = data.get('phone')
        task_name = data.get('task_name')
        task_id = data.get('task_id')
        name = data.get('name')

        document = add_document_to_pending_task(phone, task_name, task_id, name)
        print(f"[add_document_to_task] Added document to pending task: {document}")

        handle_send(f'У вас новый документ "{name}" для задачи "{task_name}"', phone)

        if document:
            return jsonify({'id': document.id, 'name': document.name, 'status': document.status}), 200
        else:
            return jsonify({'error': 'Pending task not found or already completed'}), 404
    except Exception as e:
        print(f"[add_document_to_task] Exception: {e}")
        return jsonify({'error': str(e)}), 500

# GET
# получение рассылки
@app.route('/mailing/user', methods=['GET'])
def get_mailings_status_by_user_id_route():
    try:
        data = request.json
        print(f"[get_mailings_status_by_user_id_route] Received data: {data}")

        phone = data.get('phone')
        task_id = data.get('task_id')

        mailings = get_mailings_by_phone_and_task_id(phone, task_id)
        print(f"[get_mailings_status_by_user_id_route] Retrieved mailings: {mailings}")
        return jsonify([{'id': mailing.id, 'task_name': mailing.task_name, 'message_text': mailing.message_text, 'status': mailing.status} for mailing in mailings]), 200
    except Exception as e:
        print(f"[get_mailings_status_by_user_id_route] Exception: {e}")
        return jsonify({'error': str(e)}), 500

# получение документа
@app.route('/document/mailing/user', methods=['GET'])
def get_documents_by_document_id_route():
    try:
        data = request.json
        print(f"[get_documents_by_document_id_route] Received data: {data}")

        phone = data.get('phone')
        task_id = data.get('task_id')
        name = data.get('name')

        document = get_documents_by_task_and_name_and_phone(phone, task_id, name)
        print(f"[get_documents_by_document_id_route] Retrieved document: {document}")
        
        if document:
            return jsonify({'id': document.id, 'name': document.name, 'status': document.status}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        print(f"[get_documents_by_document_id_route] Exception: {e}")
        return jsonify({'error': str(e)}), 500

def start_api():
    print(f"[start_api] Starting API on {bot_host}:{bot_port}")
    app.run(host=bot_host, port=bot_port)

# Запуск приложения
if __name__ == '__main__':
    start_api()
