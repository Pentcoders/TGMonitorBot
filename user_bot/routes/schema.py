from pydantic import BaseModel

class UserAuthorized(BaseModel):
    user_uuid: str
    code_auth: str


class CardMonitoring(BaseModel):
    user_uuid: str
    card_uuid: str


class ManyCardsMonitoring(BaseModel):
    user_uuid: str
    card_uuid: list[str]