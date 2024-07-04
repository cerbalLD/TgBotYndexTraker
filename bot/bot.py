import telebot
from telebot import types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models import Base
from bot.database_operations import (
    add_user,
    update_user_chat_id,
    update_mailing_status,
    update_document_status,
    update_user_phone,
    get_user_by_phone,
    get_user_by_chat_id,
    get_mailing_by_id,
    get_pending_mailings_by_user_id,
    get_pending_documents_by_mailing_id,
    get_documents_by_document_id
)
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

# Инициализация бота Telegram
bot_token = config['telegram_token']
bot = telebot.TeleBot(bot_token)

# Инициализация базы данных SQLAlchemy
engine = create_engine('sqlite:///bot.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    print(f"[start_message] Handling /start command for chat_id: {chat_id}")
        
    # Проверяем, есть ли уже пользователь с таким chat_id в базе
    user = get_user_by_chat_id(chat_id)

    if user:
        handle_main_menu(message)
    else:
        reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(reg_button)

        bot.send_message(chat_id, text='Отправьте номер телефона чтобы мы могли связаться с вами потом.', reply_markup=keyboard)

# Главное меню
@bot.message_handler(func=lambda message: message.text == "Проверить нужно ли отправить документы")
def handle_main_menu(message):
    chat_id = message.chat.id
    print(f"[handle_main_menu] Handling main menu for chat_id: {chat_id}")

    user = get_user_by_chat_id(chat_id)
    if not user:
        start_message(message)
    user_id = user.id

    # Получаем сообщения что нужно отправить
    mailings = get_pending_mailings_by_user_id(user_id)

    if mailings:
        handle_send_documents(message)
    else:
        # Если нет не отправленных документов
        search_button = types.KeyboardButton(text="Проверить нужно ли отправить документы")

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(search_button)

        bot.send_message(chat_id, text="У вас пока нету не отправленых документов.", reply_markup=keyboard)

# Получение контакта
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        phone_number = message.contact.phone_number
        chat_id = message.chat.id
        print(f"[handle_contact] Received contact from chat_id: {chat_id} with phone_number: {phone_number}")

        phone_number = phone_number.replace("+", '')
        
        # Проверяем, есть ли уже пользователь с таким chat_id в базе
        user = get_user_by_chat_id(chat_id)
        
        if user:
            update_user_phone(phone_number, chat_id)  # Обновляем номер телефона пользователя
        else:
            user = get_user_by_phone(phone_number)
            if user:
                update_user_chat_id(phone_number, chat_id) # Обновляем чат id пользователя
            else:
                add_user(phone_number, chat_id) # Создаем нового пользователя в базе данных

        bot.send_message(chat_id, text=f'Спасибо, ваш номер телефона ({phone_number}) сохранен. Теперь вы можете пользоваться ботом помошником.')
        handle_main_menu(message)

# Проверка на не отправленные документы
def handle_send_documents(message):
    chat_id = message.chat.id
    print(f"[handle_send_documents] Handling send documents for chat_id: {chat_id}")
    
    # Получаем все активные рассылки для текущего пользователя
    user = get_user_by_chat_id(chat_id)
    user_id = user.id
    mailings = get_pending_mailings_by_user_id(user_id)
    
    if mailings:
        # Создаем инлайн-клавиатуру для выбора рассылок
        keyboard = types.InlineKeyboardMarkup()
        
        for mailing in mailings:
            # Добавляем кнопку для каждой рассылки с заданием (task_name) в качестве текста кнопки
            button_text = mailing.task_name
            callback_data = f"mailing_{mailing.id}"  # Уникальный идентификатор для каждой кнопки
            
            keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
        
        # Отправляем сообщение с инлайн-клавиатурой
        bot.send_message(chat_id, "Выберите задачу для отправки документов.", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "Пока никаких документов не нужно.")

# Обработчик нажатия на кнопку задачи
@bot.callback_query_handler(func=lambda call: call.data.startswith('mailing_'))
def handle_mailing_callback(call):
    chat_id = call.message.chat.id
    mailing_id = int(call.data.split('_')[1])  # Получаем ID рассылки из callback_data
    print(f"[handle_mailing_callback] Handling mailing callback for chat_id: {chat_id} and mailing_id: {mailing_id}")

    # Получаем данные о рассылке и документах
    mailing = get_mailing_by_id(mailing_id)
    documents = get_pending_documents_by_mailing_id(mailing_id)
    
    if documents and mailing:
        # Создаем инлайн-клавиатуру для выбора документов
        keyboard = types.InlineKeyboardMarkup()

        for document in documents:
            keyboard.add(types.InlineKeyboardButton(text=document.name, callback_data=f"document_{document.id}"))

        # Добавляем кнопку для отмены
        cancel_button = types.InlineKeyboardButton(text="Назад к выбору задачи", callback_data="cancel_task")
        keyboard.add(cancel_button)

        # Отправляем сообщение с инлайн-клавиатурой для выбора документов
        bot.send_message(chat_id, f"{mailing.message_text}\nВыберите документ для отправки:", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "Больше нету документов что нужно отправить по этой задаче.")

        # Обновление статуса задачи
        update_mailing_status(mailing_id, True)

        handle_send_documents(call.message)

# Обработчик нажатия на кнопку документа
@bot.callback_query_handler(func=lambda call: call.data.startswith('document_'))
def handle_document_callback(call):
    chat_id = call.message.chat.id
    document_id = int(call.data.split('_')[1])  # Получаем ID документа из callback_data
    print(f"[handle_document_callback] Handling document callback for chat_id: {chat_id} and document_id: {document_id}")

    document = get_documents_by_document_id(document_id)

    # Добавляем кнопку для отмены
    keyboard = types.InlineKeyboardMarkup()
    mailing = get_documents_by_document_id(document_id)
    mailing_id = mailing.mailing_id
    cancel_button = types.InlineKeyboardButton(text="Назад к выбору документа", callback_data=f"cancel_{mailing_id}")
    keyboard.add(cancel_button)
    
    # Отправляем сообщение, ожидая документ
    bot.send_message(chat_id, f"Отправьте документ '{document.name}'.", reply_markup=keyboard)
    
    # Ожидаем следующее сообщение от пользователя с документом
    bot.register_next_step_handler(call.message, handle_document_sent, document_id, call, mailing, document)


# Обработчик отправки документа от пользователя
tracker_host_all = config['tracker_host_all']
save_path = config['save_path']

def handle_document_sent(message, document_id, call, mailing, document):
    chat_id = message.chat.id
    document = get_documents_by_document_id(document_id)
    print(f"[handle_document_sent] Handling document sent for chat_id: {chat_id} and document_id: {document_id}")

    try:
        # Проверяем, есть ли документ в сообщении
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            print(f"[handle_document_sent] Received document with file_id: {file_id} and file_name: {file_name}")
            
            # Получаем информацию о файле
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            
            # Загружаем файл с помощью бота
            downloaded_file = bot.download_file(file_path)
            
            # Пример сохранения файла на сервере
            file_path = os.path.join(save_path, file_name)
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # Отправка комментария о загруженном документе
            url_file = tracker_host_all + 'tracker/upload_file'
            data_file = {
                "issue_id": mailing.task_id,
                "file_path": file_path
            }
            payload_file = json.dumps(data_file)
            headers_file = {'Content-Type': 'application/json'}
            response_file = requests.post(url_file, headers=headers_file, data=payload_file)
            
            if response_file.status_code == 200:
                print('Документ успешно добавлен')
                print('Ответ сервера:')
                print(response_file.json())
            else:
                print(f'Произошла ошибка при добавлении документ: {response_file.status_code}')
                print(response_file.text)
            
            # Обновляем статус документа на True
            if document:
                update_document_status(document_id, True)
                bot.send_message(chat_id, f"Документ '{document.name}' успешно отправлен.")
        
        else:
            bot.send_message(chat_id, "Пожалуйста, отправьте документ.")
    
    except Exception as e:
        # Ловим исключение, если возникла ошибка при загрузке файла
        bot.send_message(chat_id, 'Произошла ошибка при загрузке файла')
        print(f"[handle_document_sent] Exception: {e}")
    
    finally:
        # В любом случае выполняем handle_mailing_callback(call)
        handle_mailing_callback(call)

# Переход к выбору задачи
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_task')
def handle_cancel_task_callback(call):
    chat_id = call.message.chat.id
    print(f"[handle_cancel_task_callback] Handling cancel task callback for chat_id: {chat_id}")
    bot.send_message(chat_id, "Отправка отменена.")
    # Возвращаем пользователя к выбору рассылок
    handle_send_documents(call.message)

# Переход к выбору документа
@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))
def handle_cancel_document_callback(call):
    mailing_id = int(call.data.split('_')[1])  # Получаем ID рассылки из callback_data
    print(f"[handle_cancel_document_callback] Handling cancel document callback for mailing_id: {mailing_id}")
    
    # Возвращаем пользователя к выбору документов для выбранной рассылки
    call.data = f"mailing_{mailing_id}"
    handle_mailing_callback(call)

# отправка сообщения по номеру
def handle_send(text, phone):
    user = get_user_by_phone(phone)
    print(f"[handle_send] Sending message to phone: {phone}")
    bot.send_message(user.chat_id, text)

def start_bot():
    print("[start_bot] Starting bot polling")
    bot.polling(none_stop=True)

# Запуск бота
if __name__ == '__main__':
    start_bot()
