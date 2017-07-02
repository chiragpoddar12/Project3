from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object in serializable format"""
        return{
            'name' : self.name,
            'id' : self.id
        }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    desc = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    created_on = Column(DATETIME, nullable=False)
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object in serializable format"""
        return{
            'name' : self.name,
            'id' : self.id,
            'desc' : self.desc
        }


engine = create_engine('sqlite:///catalogapp.db')


Base.metadata.create_all(engine)