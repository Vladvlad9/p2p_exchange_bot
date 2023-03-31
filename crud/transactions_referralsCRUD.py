from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import TransactionsReferrals, create_async_session
from schemas import TransactionsReferralSchema, TransactionsReferralInDBSchema


class CRUDTransactionReferrals(object):

    @staticmethod
    @create_async_session
    async def add(transaction_referral: TransactionsReferralSchema,
                  session: AsyncSession = None) -> TransactionsReferralInDBSchema | None:
        transactions_referrals = TransactionsReferrals(
            **transaction_referral.dict()
        )
        session.add(transactions_referrals)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(transactions_referrals)
            return TransactionsReferralInDBSchema(**transactions_referrals.__dict__)

    @staticmethod
    @create_async_session
    async def delete(transaction_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(TransactionsReferrals)
            .where(TransactionsReferrals.id == transaction_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(user_id: int = None,
                  transaction: int = None,
                  session: AsyncSession = None) -> TransactionsReferralInDBSchema | None:
        if user_id:
            transactions_referrals = await session.execute(
                select(TransactionsReferrals)
                .where(TransactionsReferrals.user_id == user_id).order_by(TransactionsReferrals.id)
            )
        else:
            transactions_referrals = await session.execute(
                select(TransactionsReferrals)
                .where(TransactionsReferrals.id == transaction).order_by(TransactionsReferrals.id)
            )
        if transaction_referral := transactions_referrals.first():
            return TransactionsReferralInDBSchema(**transaction_referral[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(referral_id: int = None,
                      session: AsyncSession = None) -> list[TransactionsReferralInDBSchema]:
        try:
            if referral_id:
                users = await session.execute(
                    select(TransactionsReferrals).where(TransactionsReferrals.referral_id == referral_id)
                        .order_by(TransactionsReferrals.id)
                )
            else:
                users = await session.execute(
                    select(TransactionsReferrals).order_by(TransactionsReferrals.id)
                )
            return [TransactionsReferralInDBSchema(**user[0].__dict__) for user in users]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(transaction_referral: TransactionsReferralInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(TransactionsReferrals)
            .where(TransactionsReferrals.id == transaction_referral.id)
            .values(**transaction_referral.dict())
        )
        await session.commit()
