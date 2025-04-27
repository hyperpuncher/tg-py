from pydantic import BaseModel, Field


class TgUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class TgPhoto(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int


class TgMessage(BaseModel):
    message_id: int
    chat: TgUser
    text: str | None = None
    photo: list[TgPhoto] | None = None
    reply_to_message: "TgMessage | None" = None


class TgReplyParameters(BaseModel):
    message_id: int
    chat_id: int | None = None


class TgMessageData(BaseModel):
    chat_id: int
    message_id: int | None = None
    text: str
    parse_mode: str | None = None
    reply_markup: dict | None = None
    reply_parameters: TgReplyParameters | None = None
    link_preview_options: dict = {"is_disabled": True}


class TgCallbackQuery(BaseModel):
    id: str
    user: TgUser = Field(alias="from")
    message: TgMessage
    data: str | None = None


class TgUpdate(BaseModel):
    update_id: int
    message: TgMessage | None = None
    callback_query: TgCallbackQuery | None = None


class TgUpdates(BaseModel):
    ok: bool
    result: list[TgUpdate] = []
