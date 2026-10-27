
import re
import urllib.request
from html import unescape

URL = "https://app.monta.app/d/cp2769835"

request = urllib.request.Request(
    URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(
    request, timeout=20
) as response:
    html = response.read().decode("utf-8")

matches = re.findall(
    r'<span\b[^>]*data-slot=["\']badge["\'][^>]*>'
    r'\s*([^<]+)\s*</span>',
    html,
    flags=re.IGNORECASE
)

statuses = [unescape(s).strip() for s in matches]

print("Status badges found:", statuses)

if statuses:
    charger_status = statuses[0]
    print("Charger status:", charger_status)
    print("Other badges:", statuses[1:])
else:
    print("No charger status found")
