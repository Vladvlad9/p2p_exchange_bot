from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]
    BOT_LINK: str


class PaymentSchema(BaseModel):
    REQUISITES: int


class ConfigSchema(BaseModel):
    BOT: BotSchema
    PAYMENT: PaymentSchema
    DATABASE: str
    COINBASE: str
    COMMISSION: str
