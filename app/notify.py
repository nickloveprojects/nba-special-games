import logging
import os

import requests

from .output import to_text

log = logging.getLogger("nba")


def send(slate: dict):
    text = to_text(slate)
    url = os.getenv("DISCORD_WEBHOOK_URL")
    tok, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if url:
        for i in range(0, len(text), 1900):  # Discord 2000-char limit
            requests.post(url, json={"content": text[i:i + 1900]}, timeout=20).raise_for_status()
    if tok and chat:
        for i in range(0, len(text), 3900):  # Telegram 4096-char limit
            requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                          json={"chat_id": chat, "text": text[i:i + 3900]}, timeout=20).raise_for_status()
    if not (url or (tok and chat)):
        log.info("No notification channel configured; skipping")
