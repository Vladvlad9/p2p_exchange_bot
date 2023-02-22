from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]
    BOT_LINK: str


class PaymentSchema(BaseModel):
    REQUISITES: int


class CommissionSchema(BaseModel):
    COMMISSION_BOT: int
    COMMISSION_REFERRAL: int


class CoinbaseSchema(BaseModel):
    BYN: str
    USD: str
    RUB: str


class ConfigSchema(BaseModel):
    BOT: BotSchema
    PAYMENT: PaymentSchema
    COMMISSION: CommissionSchema
    COINBASE: CoinbaseSchema

    DATABASE: str
