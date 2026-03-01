# init_session_qr.py
import telethon
from telethon import TelegramClient
from qrcode import QRCode
from base64 import urlsafe_b64encode as base64url
import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()  # ← Добавьте эту строку

qr = QRCode()

def gen_qr(token: str):
    qr.clear()
    qr.add_data(token)
    qr.print_ascii()

def display_url_as_qr(url):
    print(url)
    gen_qr(url)

async def main(client: telethon.TelegramClient):
    if not client.is_connected():
        await client.connect()

    qr_login = await client.qr_login()

    print("Scan this QR code with your Telegram app:")
    r = False
    while not r:
        display_url_as_qr(qr_login.url)
        try:
            r = await qr_login.wait(10)
        except:
            await qr_login.recreate()

    print("✅ Successfully logged in via QR code!")

TELEGRAM_API_ID = int(os.getenv("TG_API_ID"))
TELEGRAM_API_HASH = os.getenv("TG_API_HASH")
PHONE = os.getenv("TG_PHONE")

client = TelegramClient("mfin", TELEGRAM_API_ID, TELEGRAM_API_HASH)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main(client))