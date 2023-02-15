from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ApplicantForm(Base):
    __tablename__: str = "applicant_forms"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    phone_number = Column(CHAR(12), nullable=True)
    clas = Column(Integer, nullable=False)
    answer_to_quiz = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True)
    date_created = Column(TIMESTAMP, default=datetime.now())


