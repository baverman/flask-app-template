from sqlalchemy import Column, String, Integer, Text, Boolean
from . import Base


class Value(Base):
    __tablename__ = 'vals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer)
