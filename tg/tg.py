import re
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from .models import (
    TgMessageData,
    TgUpdates,
)
from .net import client


@retry(
    retry=retry_if_exception_type(httpx.ConnectTimeout),
    stop=stop_after_attempt(10),
)
async def get_updates(offset: int) -> TgUpdates | None:
    params = {"timeout": 50, "offset": offset}

    try:
        r = await client.get("getUpdates", params=params)
        r.raise_for_status()
        return TgUpdates(**r.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}")
    except httpx.ConnectTimeout:
        print("Connection timed out.")
    return None


@retry(
    retry=retry_if_exception_type(httpx.ConnectTimeout),
    stop=stop_after_attempt(10),
)
async def send_message(data: TgMessageData):
    # Remove all tags except <b>, <i>, <u>, and <a>
    pattern = re.compile(r"<(?!\/?(b|i|u|a)\b)[^>]*>")
    data.text = pattern.sub("", data.text)

    # Remove markdown
    pattern = re.compile(r"!\[.*?\]\(.*?\)\n?")
    data.text = pattern.sub("", data.text)
    data.text = data.text.replace("### ", "").replace("## ", "")

    url = "sendMessage" if not data.message_id else "editMessageText"
    messages = []
    max_length = 4000

    if len(data.text) > max_length:
        message = ""
        for line in data.text.splitlines():
            if len(message + line) <= max_length:
                message += line + "\n"
            else:
                messages.append(message)
                message = line
    else:
        messages.append(data.text)

    for message in messages:
        data.text = message
        r = await client.post(url, json=data.model_dump(exclude_none=True))
        r.raise_for_status()


@retry(
    retry=retry_if_exception_type(httpx.ConnectTimeout),
    stop=stop_after_attempt(10),
)
async def edit_message(
    chat_id: int, message_id: int, text: str, parse_mode: str | None = None
):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    await client.post("editMessageText", json=data)


@retry(
    retry=retry_if_exception_type(httpx.ConnectTimeout),
    stop=stop_after_attempt(10),
)
async def delete_message(chat_id: int, message_id: int):
    data = {"chat_id": chat_id, "message_id": message_id}
    await client.post("deleteMessage", data=data)


@retry(stop=stop_after_attempt(10))
async def send_photo(chat_id: int, photos: list[dict[str, Any]]):
    r = await client.post(
        "sendMediaGroup",
        json={"chat_id": chat_id, "media": photos},
    )
    if r.status_code == 200:
        return "Photos sent"


async def get_file_url(file_id: str, bot_token: str) -> str | None:
    r = await client.post(
        "getFile",
        data={"file_id": file_id},
    )

    if r.status_code == 200:
        return (
            "https://api.telegram.org/file/bot"
            + bot_token
            + r.json()["result"]["file_path"]
        )


@retry(stop=stop_after_attempt(10))
async def send_typing_status(chat_id: int):
    data = {"chat_id": chat_id, "action": "typing"}
    await client.post("sendChatAction", data=data)
