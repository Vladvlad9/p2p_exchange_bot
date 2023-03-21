from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Verification, create_async_session
from schemas import VerificationSchema, VerificationInDBSchema


class CRUDVerification(object):

    @staticmethod
    @create_async_session
    async def add(verification: VerificationSchema, session: AsyncSession = None) -> VerificationInDBSchema | None:
        verifications = Verification(
            **verification.dict()
        )
        session.add(verifications)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(verifications)
            return VerificationInDBSchema(**verifications.__dict__)

    @staticmethod
    @create_async_session
    async def delete(verification_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Verification)
            .where(Verification.id == verification_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(user_id: int = None,
                  session: AsyncSession = None) -> VerificationInDBSchema | None:
        verifications = await session.execute(
            select(Verification)
                .where(Verification.user_id == user_id)
        )
        if verification := verifications.first():
            return VerificationInDBSchema(**verification[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[VerificationInDBSchema]:
        try:
            verifications = await session.execute(
                select(Verification)
                .order_by(Verification.id)
            )
            return [VerificationInDBSchema(**verification[0].__dict__) for verification in verifications]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(verification: VerificationInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Verification)
            .where(Verification.id == verification.id)
            .values(**verification.dict())
        )
        await session.commit()
