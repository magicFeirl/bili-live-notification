import asyncio
import logging
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass

# telegram.Bot 是用于主动发送消息的核心类 (PTB v20+)
from telegram import Bot
from telegram.error import Forbidden, NetworkError


async def send_notification(
    bot: Bot, users: list[PushUser], streamer: Streamer, title: str, cover_url: str
):
    message = f"🔴 *{streamer.name} 开播啦！*\n\n📺 标题：{title}\n⏰ 时间：{datetime.now().strftime('%H:%M:%S')}"

    for user in users:
        try:
            if cover_url:
                await bot.send_photo(
                    chat_id=user.uid,
                    photo=cover_url,
                    caption=message,
                    parse_mode="Markdown",
                )
            else:
                await bot.send_message(
                    chat_id=user.uid, text=message, parse_mode="Markdown"
                )
        except Exception:
            continue
