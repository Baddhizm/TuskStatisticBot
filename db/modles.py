from sqlalchemy import Integer, Column, VARCHAR, TIMESTAMP

from db import Base, engine


class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    hand = Column(VARCHAR(1))
    systolic = Column(Integer)
    diastolic = Column(Integer)
    pulse = Column(Integer, default=None)
    comment = Column(VARCHAR(255))
    date = Column(TIMESTAMP)


# Create all tables if not exist
Base.metadata.create_all(engine)
