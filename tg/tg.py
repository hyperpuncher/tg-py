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
async def send_message(
    chat_id: int | str,
    text: str,
    message_id: int | None = None,
    parse_mode: str | None = None,
    reply_markup: dict | None = None,
    reply_parameters: dict | None = None,
    link_preview_options: dict = {"is_disabled": True},
):
    # Remove all tags except <b>, <i>, <u>, and <a>
    pattern = re.compile(r"<(?!\/?(b|i|u|a)\b)[^>]*>")
    text = pattern.sub("", text)

    # Remove markdown
    pattern = re.compile(r"!\[.*?\]\(.*?\)\n?")
    text = pattern.sub("", text)
    text = text.replace("### ", "").replace("## ", "")

    url = "sendMessage" if not message_id else "editMessageText"
    messages = []
    max_length = 4000

    if len(text) > max_length:
        message = ""
        for line in text.splitlines():
            if len(message + line) <= max_length:
                message += line + "\n"
            else:
                messages.append(message)
                message = line
    else:
        messages.append(text)

    for message in messages:
        json = {
            "chat_id": chat_id,
            "text": message,
            "message_id": message_id,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
            "reply_parameters": reply_parameters,
            "link_preview_options": link_preview_options,
        }
        json = {k: v for k, v in json.items() if v is not None}

        r = await client.post(url, json=json)
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
