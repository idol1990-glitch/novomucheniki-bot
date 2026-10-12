"""
Бот «Новомученик дня».
Каждый день постит святых этой даты: список в родительном,
житие последнего и его икону.

Файлы рядом со скриптом:
  novomucheniki_posts.json
  nm_icons/

Запуск:
  set BOT_TOKEN=123456:ABC...
  set CHAT_ID=@my_channel
  set POST_HOUR=18
  set POST_MINUTE=0
  pip install python-telegram-bot==21.6
  python bot.py
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import Bot

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
HOUR = int(os.environ.get("POST_HOUR", "18"))
MINUTE = int(os.environ.get("POST_MINUTE", "0"))
TZ = ZoneInfo(os.environ.get("TZ_NAME", "Europe/Moscow"))

BASE = Path(__file__).parent
POSTS_PATH = BASE / "novomucheniki_posts.json"
ICON_DIR = BASE / "nm_icons"
CAPTION_LIMIT = 1024


def today_post():
    data = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    now = datetime.now(TZ)
    key = f"{now.day:02d}.{now.month:02d}"
    for post in data["posts"]:
        if post["date"] == key:
            return post
    return None


async def publish():
    post = today_post()
    bot = Bot(TOKEN)
    if not post:
        print("сегодня новомучеников нет")
        return
    caption = post.get("caption") or post.get("names") or ""
    if len(caption) > CAPTION_LIMIT:
        caption = caption[: CAPTION_LIMIT - 1].rsplit(" ", 1)[0] + "…"
    icon = ICON_DIR / post["icon"] if post.get("icon") else None
    if icon and icon.exists():
        with icon.open("rb") as f:
            await bot.send_photo(CHAT_ID, f, caption=caption)
    else:
        await bot.send_message(CHAT_ID, caption)
    print("отправлено", post["date"], post.get("life_name"))


def main():
    now = datetime.now(TZ)
    target = now.replace(hour=HOUR, minute=MINUTE, second=0, microsecond=0)
    delay = (target - now).total_seconds()
    if delay < 0:
        delay += 86400
    print(f"жду до {HOUR:02d}:{MINUTE:02d} ({TZ}), через {int(delay)} с")
    import time
    time.sleep(delay)
    asyncio.run(publish())


if __name__ == "__main__":
    # разово, без ожидания: python bot.py now
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        asyncio.run(publish())
    else:
        main()
