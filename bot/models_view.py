from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Mailing, Document

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
view_host = config['view_host']
view_port = config['view_port']

# Инициализация Flask
app = Flask(__name__)
app.secret_key = '\xfd{H\xe5&lt;\x95\xf9\xe3\x96.5\xd1\x01O&lt;!\xd5\xa2\xa0\x9fR"\xa1\xa8'

# Инициализация базы данных
engine = create_engine('sqlite:///bot.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Инициализация Flask-Admin
admin = Admin(app, name='Bot Admin', template_mode='bootstrap3')

# Определим кастомные ModelView для каждой модели

class UserView(ModelView):
    column_list = ['id', 'phone', 'telegram_id']
    form_columns = ['phone', 'telegram_id']

class MailingView(ModelView):
    column_list = ['id', 'user', 'task_name', 'message_text', 'status', 'task_id']
    form_columns = ['user', 'task_name', 'message_text', 'status', 'task_id']

class DocumentView(ModelView):
    column_list = ['id', 'name', 'status', 'mailing']
    form_columns = ['name', 'status', 'mailing']

# Добавляем представления к админ-панели
admin.add_view(UserView(User, session))
admin.add_view(MailingView(Mailing, session))
admin.add_view(DocumentView(Document, session))

if __name__ == '__main__':
   app.run(host=view_host, port=view_port)
