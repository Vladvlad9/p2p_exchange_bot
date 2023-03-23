from pydantic import BaseModel


class MAIN_FORM(BaseModel):
    TEXT: str


class FIRST_PAGE(BaseModel):
    TEXT: str


class Requisites(BaseModel):
    TEXT: str


class ConfigTextSchema(BaseModel):
    MAIN_FORM: MAIN_FORM
    FIRST_PAGE: FIRST_PAGE
    Requisites: Requisites
