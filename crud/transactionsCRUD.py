from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Transaction, create_async_session
from schemas import TransactionSchema, TransactionInDBSchema


class CRUDTransaction(object):

    @staticmethod
    @create_async_session
    async def add(transaction: TransactionSchema, session: AsyncSession = None) -> TransactionInDBSchema | None:
        transactions = Transaction(
            **transaction.dict()
        )
        session.add(transactions)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(transactions)
            return TransactionInDBSchema(**transactions.__dict__)

    @staticmethod
    @create_async_session
    async def delete(transaction_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Transaction)
            .where(Transaction.id == transaction_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(user_id: int,
                  session: AsyncSession = None) -> TransactionInDBSchema | None:
        transactions = await session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
        )
        if transaction := transactions.first():
            return TransactionInDBSchema(**transaction[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[TransactionInDBSchema]:
        try:
            users = await session.execute(
                select(Transaction)
            )
            return [TransactionInDBSchema(**user[0].__dict__) for user in users]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(user: TransactionInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Transaction)
            .where(Transaction.id == user.id)
            .values(**user.dict())
        )
        await session.commit()