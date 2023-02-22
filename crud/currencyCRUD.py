from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Currency, create_async_session
from schemas import CurrencyInDBSchema


class CRUDCurrency(object):

    @staticmethod
    @create_async_session
    async def get(currency_id: int = None, currency_name: str = None,
                  session: AsyncSession = None) -> CurrencyInDBSchema | None:
        if currency_id:
            transactions = await session.execute(
                select(Currency)
                    .where(Currency.id == currency_id)
            )
        else:
            transactions = await session.execute(
                select(Currency)
                    .where(Currency.name == currency_name)
            )
        if transaction := transactions.first():
            return CurrencyInDBSchema(**transaction[0].__dict__)

