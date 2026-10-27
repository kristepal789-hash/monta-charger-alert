import os, re, json, urllib.request
from pathlib import Path

URL='https://app.monta.app/d/cp2769835'
STATE=Path('last_status.txt')

def notify(message):
    token=os.environ.get('TELEGRAM_BOT_TOKEN')
    chat=os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat:
        raise RuntimeError('Telegram secrets missing')
    data=json.dumps({'chat_id':chat,'text':message}).encode()
    req=urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage',data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r:
        result=json.load(r)
    if not result.get('ok'): raise RuntimeError('Telegram API rejected message')

req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=25) as r:
    html=r.read().decode('utf-8','replace')
# Deliberately conservative: generic words in scripts/metadata do not prove live status.
# This is a diagnostic probe, not a verified live-status integration.
print('Fetched webpage:',len(html),'characters')
print('Contains Busy:',bool(re.search(r'\bbusy\b',html,re.I)))
print('Contains Available:',bool(re.search(r'\bavailable\b',html,re.I)))
print('Live status extraction NOT VERIFIED; no availability alert sent.')
if os.environ.get('SEND_TEST')=='1':
    notify('Monta alert test successful. Live charger status monitoring is NOT configured yet.')
