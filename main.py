import requests
from bs4 import BeautifulSoup
import time
import schedule
from telegram import Bot

BOT_TOKEN = "BURAYA_BOT_TOKEN"
CHAT_ID = "BURAYA_GRUP_ID"

bot = Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# TRENDYOL SCRAPER
def trendyol_firsatlar():
    url = "https://www.trendyol.com/sr?fl=fiyatidusenler"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ürünler = soup.select(".p-card-wrppr")

    sonuçlar = []

    for u in ürünler[:10]:  # ilk 10 üründen limit
        try:
            ad = u.select_one(".prdct-desc-cntnr").text.strip()
            fiyat = u.select_one(".prc-box-dscntd").text.strip()
            eski = u.select_one(".prc-box-orgnl").text.strip() if u.select_one(".prc-box-orgnl") else None
            link = "https://www.trendyol.com" + u.a["href"]

            if eski:
                eski_f = float(eski.replace("TL", "").replace(",", "."))
                yeni_f = float(fiyat.replace("TL", "").replace(",", "."))
                indirim = int((1 - yeni_f / eski_f) * 100)

                if indirim >= 20:
                    sonuçlar.append(f"🔥 *{ad}*\nEski: {eski}\nYeni: {fiyat}\nİndirim: %{indirim}\n🔗 {link}")

        except:
            pass
    
    return sonuçlar


# AMAZON SCRAPER
def amazon_firsatlar():
    url = "https://www.amazon.com.tr/gp/goldbox"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ürünler = soup.select(".a-section.a-text-center")

    sonuçlar = []

    for u in ürünler[:5]:
        try:
            ad = u.select_one("img")["alt"]
            link = "https://www.amazon.com.tr" + u.select_one("a")["href"]

            sonuçlar.append(f"🔵 *{ad}*\n🔗 {link}")

        except:
            pass
    
    return sonuçlar


# HEPSİBURADA SCRAPER
def hepsiburada_firsatlar():
    url = "https://www.hepsiburada.com/kampanyalar"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    sonuçlar = []
    kampanyalar = soup.select("a.campaign-card__title")

    for k in kampanyalar[:5]:
        try:
            ad = k.text.strip()
            link = "https://www.hepsiburada.com" + k["href"]
            sonuçlar.append(f"🟢 *{ad}*\n🔗 {link}")
        except:
            pass
    
    return sonuçlar


# N11 SCRAPER
def n11_firsatlar():
    url = "https://www.n11.com/gunun-firsatlari"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    sonuçlar = []
    ürünler = soup.select(".productName")

    for u in ürünler[:5]:
        try:
            ad = u.text.strip()
            sonuçlar.append(f"🟣 *{ad}*\n🔗 https://www.n11.com/gunun-firsatlari")
        except:
            pass

    return sonuçlar


# MESAJ GÖNDERİCİ
def gönder():
    mesajlar = []

    mesajlar += trendyol_firsatlar()
    mesajlar += amazon_firsatlar()
    mesajlar += hepsiburada_firsatlar()
    mesajlar += n11_firsatlar()

    if not mesajlar:
        return

    for mesaj in mesajlar:
        bot.send_message(chat_id=CHAT_ID, text=mesaj, parse_mode="Markdown")
        time.sleep(2)


# HER 30 DAKİKADA ÇALIŞTIR
schedule.every(30).minutes.do(gönder)

print("Bot çalışıyor...")

while True:
    schedule.run_pending()
    time.sleep(1)
