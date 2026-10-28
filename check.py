
import json
import os
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

URL = "https://app.monta.app/d/cp2769835"
STATE = Path("charger_state.json")
VALID = {"busy", "available"}


def telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat:
        raise RuntimeError(
            "Missing Telegram token or chat ID in GitHub secrets"
        )

    data = urllib.parse.urlencode({
        "chat_id": chat,
        "text": message
    }).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.load(response)
    except Exception as exc:
        raise RuntimeError(
            "Telegram failed. Check token, chat ID and bot Start."
        ) from exc

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected the message")

    print("Telegram notification delivered")


def get_status():
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=25) as response:
        html = response.read().decode("utf-8")

    badges = re.findall(
        r'<span\b[^>]*data-slot=["\']badge["\'][^>]*>'
        r'\s*([^<]+)\s*</span>',
        html,
        re.I
    )

    badges = [unescape(s).strip() for s in badges]
    print("Badges:", badges)

    if not badges or badges[0].lower() not in VALID:
        raise RuntimeError("Unrecognized charger status")

    return badges[0].lower()


def main():
    if os.environ.get("TEST_TELEGRAM", "false").lower() == "true":
        telegram("Monta charger alert: Telegram test successful.")
        return

    current = get_status()
    previous = None

    if STATE.exists():
        previous = json.loads(STATE.read_text()).get("status")

    print("Previous:", previous, "Current:", current)

    if previous in VALID and previous != current:
        status = "AVAILABLE" if current == "available" else "BUSY"

        telegram(
            f"Monta charger is now {status}!\n"
            f"Universitetsparken 2\n{URL}"
        )

    elif previous is None:
        print("First run: saving initial status")

    else:
        print("No change: no notification")

    STATE.write_text(json.dumps({"status": current}))


if __name__ == "__main__":
    main()
