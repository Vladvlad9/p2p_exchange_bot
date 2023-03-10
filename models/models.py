from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger, \
    Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date_created = Column(TIMESTAMP, default=datetime.now())  # Дата создания акк.


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False)
    exchange_rate = Column(Float, default=0)  # курс обмена
    buy_BTC = Column(Float, default=0)
    sale = Column(Float, default=0)
    currency_id = Column(Integer, ForeignKey("currency.id", ondelete="NO ACTION"), nullable=False)
    wallet = Column(Text, default=None)
    date_created = Column(TIMESTAMP, default=datetime.now())
    approved = Column(Boolean, default=False)
    check = Column(Text, default="None")


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False)
    referral_id = Column(BigInteger, default=True)


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False)
    address = Column(Text)
    wif = Column(Text)

