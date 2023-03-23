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
    MIN_BYN: int
    MIN_RUB: int


class CoinbaseSchema(BaseModel):
    BYN: str
    USD: str
    RUB: str
    BTC_BYN: str
    BTC_RUB: str


class BlockIoSchemas(BaseModel):
    API_KEY: str
    SECRET_PIN: str
    VERSION: int


class ConfigSchema(BaseModel):
    BOT: BotSchema
    PAYMENT: PaymentSchema
    COMMISSION: CommissionSchema
    COINBASE: CoinbaseSchema
    BLOCK_IO: BlockIoSchemas

    PAYMENT_TIMER: int

    DATABASE: str
