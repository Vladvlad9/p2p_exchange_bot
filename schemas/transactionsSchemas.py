from datetime import datetime
from pydantic import BaseModel, Field


class TransactionSchema(BaseModel):
    user_id: int = Field(ge=1)
    exchange_rate: float = Field(default=0)
    buy_BTC: float = Field(default=0)
    sale: float = Field(default=0)
    currency_id: int = Field(default=0)
    wallet: str = Field(default=None)
    date_created: datetime = Field(default=datetime.now())
    approved: bool = Field(default=False)
    check: str = Field(default="None")


class TransactionInDBSchema(TransactionSchema):
    id: int = Field(ge=1)
