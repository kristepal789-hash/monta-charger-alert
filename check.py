
import os
import re
import json
import urllib.request
import urllib.parse
from html import unescape
from pathlib import Path

URL = "https://app.monta.app/d/cp2769835"
STATE_FILE = Path("charger_state.json")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram secrets missing")
        return

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=20):
        print("Telegram notification sent")


def get_status():
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8")

    matches = re.findall(
        r'<span\b[^>]*data-slot=["\']badge["\'][^>]*>'
        r'\s*([^<]+)\s*</span>',
        html,
        flags=re.IGNORECASE
    )

    statuses = [unescape(s).strip() for s in matches]

    if not statuses:
        raise RuntimeError("Charger status not found")

    return statuses[0]


def main():
    current = get_status()
    print("Current charger status:", current)

    previous = None

    if STATE_FILE.exists():
        previous = json.loads(
            STATE_FILE.read_text()
        ).get("status")

    print("Previous status:", previous)

    if current.lower() == "available" and previous != "Available":
        send_telegram(
            "Monta charger is AVAILABLE!\n"
            "Universitetsparken 2\n"
            f"{URL}"
        )

    STATE_FILE.write_text(
        json.dumps({"status": current})
    )


if __name__ == "__main__":
    main()
