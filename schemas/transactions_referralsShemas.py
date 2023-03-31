from datetime import datetime
from pydantic import BaseModel, Field


class TransactionsReferralSchema(BaseModel):
    transaction_id: int = Field(ge=1)
    percent: float
    referral_id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    date_transaction: datetime = Field(default=datetime.now())


class TransactionsReferralInDBSchema(TransactionsReferralSchema):
    id: int = Field(ge=1)
