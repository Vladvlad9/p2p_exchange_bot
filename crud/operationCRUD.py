from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Operation, create_async_session
from schemas import OperationSchema


class CRUDOperation(object):

    @staticmethod
    @create_async_session
    async def get(operation_id: int = None, operation_name: str = None,
                  session: AsyncSession = None) -> OperationSchema | None:
        if operation_id:
            operations = await session.execute(
                select(Operation)
                    .where(Operation.id == operation_id)
            )
        else:
            operations = await session.execute(
                select(Operation)
                    .where(Operation.name == operation_name)
            )
        if operation := operations.first():
            return OperationSchema(**operation[0].__dict__)

