from pydantic import BaseModel, Field


class WalletSchema(BaseModel):
    user_id: int = Field(ge=1)
    address: str
    wif: str
    passphrase: str


class WalletInDBSchema(WalletSchema):
    id: int = Field(ge=1)
