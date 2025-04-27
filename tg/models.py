from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class Photo(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int


class Message(BaseModel):
    message_id: int
    chat: User
    text: str | None = None
    photo: list[Photo] | None = None
    reply_to_message: "Message | None" = None


class ReplyParameters(BaseModel):
    message_id: int
    chat_id: int | str | None = None


class MessageData(BaseModel):
    chat_id: int | str
    message_id: int | None = None
    text: str
    parse_mode: str | None = None
    reply_markup: dict | None = None
    reply_parameters: ReplyParameters | None = None
    link_preview_options: dict = {"is_disabled": True}


class CallbackQuery(BaseModel):
    id: str
    user: User = Field(alias="from")
    message: Message
    data: str | None = None


class Update(BaseModel):
    update_id: int
    message: Message | None = None
    callback_query: CallbackQuery | None = None


class Updates(BaseModel):
    ok: bool
    result: list[Update] = []
