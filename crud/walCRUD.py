from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Wallet, create_async_session
from schemas import WalletSchema, WalletInDBSchema


class CRUDWallet(object):

    @staticmethod
    @create_async_session
    async def add(wallet: WalletSchema, session: AsyncSession = None) -> WalletInDBSchema | None:
        wallets = Wallet(
            **wallet.dict()
        )
        session.add(wallets)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(wallets)
            return WalletInDBSchema(**wallets.__dict__)

    @staticmethod
    @create_async_session
    async def get(user_id: int = None,
                  session: AsyncSession = None) -> WalletInDBSchema | None:
        wallets = await session.execute(
            select(Wallet)
            .where(Wallet.user_id == user_id)
        )
        if wallet := wallets.first():
            return WalletInDBSchema(**wallet[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[WalletInDBSchema]:
        try:
            wallets = await session.execute(
                select(Wallet)
                    .order_by(Wallet.id)
            )
            return [WalletInDBSchema(**wallet[0].__dict__) for wallet in wallets]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(wallet: WalletInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Wallet)
            .where(Wallet.id == wallet.id)
            .values(**wallet.dict())
        )
        await session.commit()
