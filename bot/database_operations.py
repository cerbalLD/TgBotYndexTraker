from sqlalchemy.orm import sessionmaker, joinedload
from bot.models import engine, User, Mailing, Document

Session = sessionmaker(bind=engine)
session = Session()

# Функции для добавления данных
def add_user(phone, chat_id=None, date='9:00'):
    user = User(phone=phone, chat_id=chat_id, date=date)
    session.add(user)
    session.commit()
    return user

# Функции для обновления данных
def update_user_chat_id(phone, chat_id):
    user = session.query(User).filter_by(phone=phone).all()
    user = user[0]
    if user:
        user.chat_id = chat_id
        session.commit()
        return user
    else:
        return None
    
def update_user_phone(phone, chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).all()
    user = user[0]
    if user:
        user.phone = phone
        session.commit()
        return user
    else:
        return None 

def update_mailing_status(mailing_id, status):
    mailing = session.query(Mailing).filter_by(id=mailing_id).all()
    mailing = mailing[0]
    if mailing:
        mailing.status = status
        session.commit()
        return mailing
    else:
        return None
    
def update_document_status(document_id, status):
    document = session.query(Document).filter_by(id=document_id).all()
    document = document[0]
    if document:
        document.status = status
        session.commit()
        return document
    else:
        return None
    
# Функции для получения данных
def get_user_by_phone(phone):
    return session.query(User).filter_by(phone=phone).first()

def get_user_by_chat_id(chat_id):
    return session.query(User).filter_by(chat_id=chat_id).first()

def get_mailing_by_id(mailing_id):
    return session.query(Mailing).filter_by(id=mailing_id).first()

def get_pending_mailings_by_user_id(user_id):
    return session.query(Mailing).filter_by(user_id=user_id, status=False).all()

def get_documents_by_document_id(document_id):
    return session.query(Document).filter_by(id=document_id).first()

def get_pending_documents_by_mailing_id(mailing_id):
    return session.query(Document).filter_by(mailing_id=mailing_id, status=False).all()



# для api
# Функции для добавления данных
def add_mailing(user_id, task_name, message_text, task_id, status=False):
    mailing = Mailing(user_id=user_id, task_name=task_name, message_text=message_text, status=status, task_id=task_id)
    session.add(mailing)
    session.commit()
    return mailing

def add_document(name, mailing_id, status=False):
    document = Document(name=name, mailing_id=mailing_id, status=status)
    session.add(document)
    session.commit()
    return document

def add_document_to_pending_task(phone, task_name, task_id, name):
    mailing = session.query(Mailing).join(User).filter(
        User.phone == phone,
        Mailing.task_name == task_name,
        Mailing.task_id == task_id,
        Mailing.status == False
        ).options(joinedload(Mailing.documents)).all()
    mailing = mailing[0]
    if mailing:
        document = Document(name=name, mailing_id=mailing.id)
        session.add(document)
        session.commit()
        return document
    else:
        return None 
      
def update_user_date(phone, date):
    user = session.query(User).filter_by(phone=phone).all()
    user = user[0]
    if user:
        user.date = date
        session.commit()
        return user
    else:
        return None
    
# Функции для обновления данных
def update_mailing_status_by_task_id_and_phone(phone, task_name, task_id, status):
    mailing = session.query(Mailing).join(User).filter(
        User.phone == phone,
        Mailing.task_id == task_id,
        Mailing.task_name
        ).all()
    mailing = mailing[0]
    if mailing:
        mailing.status = status
        session.commit()
        return mailing
    else:
        return None
    
def update_document_status_by_task_and_name_and_phone(phone, task_id, name, status):
    document = session.query(Document).join(Mailing, User).filter(
        User.phone == phone,
        Mailing.task_id == task_id,
        Document.name == name,
        Mailing.status == False
    ).all()
    document = document[0]
    
    if document:
        document.status = status
        session.commit()
        return document
    else:
        return None
    
# Функции для получения данных
def get_documents_by_task_and_name_and_phone(phone, task_id, name):
    return session.query(Document).join(Mailing, User).filter(
        User.phone == phone,
        Mailing.task_id == task_id,
        Document.name == name
        ).all()

def get_mailings_by_phone_and_task_id(phone, task_id):
    return session.query(Mailing).join(User).filter(
        User.phone == phone,
        Mailing.task_id == task_id
        ).all()