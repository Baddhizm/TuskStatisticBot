import pytz
from sqlalchemy import Integer, Column, DateTime, String

from db import Base, engine


class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    hand = Column(String(1))
    systolic = Column(Integer)
    diastolic = Column(Integer)
    pulse = Column(Integer, default=None)
    comment = Column(String(255))
    date = Column(DateTime(timezone=pytz.timezone('Europe/Moscow')))


# Create all tables if not exist
Base.metadata.create_all(engine)
