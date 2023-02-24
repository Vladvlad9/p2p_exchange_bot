from pydantic import BaseModel, Field


class WalletSchema(BaseModel):
    user_id: int = Field(ge=1)
    balance: float = Field(default=0)
    address: str
    passphrase: str


class WalletInDBSchema(WalletSchema):
    id: int = Field(ge=1)
