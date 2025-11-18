import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
import os
import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0"
}

async def fetch(session, url):
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except Exception as e:
        logging.error(f"Hata: {e}")
        return None

async def trendyol():
    url = "https://www.trendyol.com/sr?fl=fiyatidusenler"
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if not html:
            logging.error("Trendyol html yok.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        ürünler = soup.select(".p-card-wrppr")
        sonuç = []

        for u in ürünler[:5]:
            try:
                ad = u.select_one(".prdct-desc-cntnr").text.strip()
                fiyat = u.select_one(".prc-box-dscntd").text.strip()
                link = "https://www.trendyol.com" + u.a["href"]
                sonuç.append(f"🔥 *{ad}*\nFiyat: {fiyat}\n🔗 {link}")
            except:
                pass

        return sonuç

async def amazon():
    url = "https://www.amazon.com.tr/gp/goldbox"
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        sonuç = []
        ürünler = soup.select("img")

        for u in ürünler[:5]:
            try:
                ad = u["alt"]
                link = "https://www.amazon.com.tr"
                sonuç.append(f"🔵 *{ad}*\n🔗 {link}")
            except:
                pass

        return sonuç

async def loop_tasks():
    while True:
        logging.info("Tarama başlıyor...")

        trendyol_list = await trendyol()
        amazon_list = await amazon()

        tüm = trendyol_list + amazon_list

        if tüm:
            for m in tüm:
                await bot.send_message(chat_id=CHAT_ID, text=m, parse_mode="Markdown")
                await asyncio.sleep(2)

        logging.info("Tarama bitti. 15 dk bekleniyor...")
        await asyncio.sleep(900)  # 15 dakika

async def main():
    await loop_tasks()

if __name__ == "__main__":
    asyncio.run(main())
