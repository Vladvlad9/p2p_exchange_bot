from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Referral, create_async_session
from schemas import ReferralSchema, ReferralInDBSchema


class CRUDReferral(object):

    @staticmethod
    @create_async_session
    async def add(referral: ReferralSchema, session: AsyncSession = None) -> ReferralInDBSchema | None:
        referrals = Referral(
            **referral.dict()
        )
        session.add(referrals)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(referrals)
            return ReferralInDBSchema(**referrals.__dict__)

    @staticmethod
    @create_async_session
    async def delete(referral_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Referral)
            .where(Referral.id == usreferral_ider_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(referral_id: int = None,
                  session: AsyncSession = None) -> ReferralInDBSchema | None:
        referrals = await session.execute(
            select(Referral)
                .where(Referral.id == referral_id)
        )
        if referral := referrals.first():
            return ReferralInDBSchema(**referral[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[ReferralInDBSchema]:
        try:
            referrals = await session.execute(
                select(Referral)
                    .order_by(Referral.id)
            )
            return [ReferralInDBSchema(**referral[0].__dict__) for referral in referrals]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(referral: ReferralInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Referral)
            .where(Referral.id == referral.id)
            .values(**referral.dict())
        )
        await session.commit()
