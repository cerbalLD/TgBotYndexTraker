from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    chat_id = Column(Integer, unique=True, nullable=True)
    date = Column(String, nullable=False)

class Mailing(Base):
    __tablename__ = 'mailings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_name = Column(String, nullable=False)
    message_text = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    task_id = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="mailings")

User.mailings = relationship("Mailing", order_by=Mailing.id, back_populates="user")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    mailing_id = Column(Integer, ForeignKey('mailings.id'), nullable=False)

    mailing = relationship("Mailing", back_populates="documents")

Mailing.documents = relationship("Document", order_by=Document.id, back_populates="mailing")

# Создание базы данных
engine = create_engine('sqlite:///bot.db')
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()
