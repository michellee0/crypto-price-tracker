import time
import sqlite3
from datetime import datetime
import requests
from plyer import notification


# 1. Veritabanı Kurulumu (SQLite)
def veritabani_hazirla():
    conn = sqlite3.connect("fiyat_gecmisi.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiyatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kripto TEXT,
            fiyat_usd REAL,
            tarih TEXT
        )
    """)
    conn.commit()
    conn.close()


# 2. Fiyat Kaydetme
def fiyati_kaydet(kripto, fiyat):
    conn = sqlite3.connect("fiyat_gecmisi.db")
    cursor = conn.cursor()
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO fiyatlar (kripto, fiyat_usd, tarih) VALUES (?, ?, ?)", (kripto, fiyat, zaman))
    conn.commit()
    conn.close()


# 3. Canlı Fiyat Çekme (CoinGecko Ücretsiz API)
def fiyat_getir(coin_id="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        veri = response.json()
        return veri[coin_id]["usd"]
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None


# 4. Windows Masaüstü Bildirimi Gönderme
def bildirim_gonder(baslik, mesaj):
    notification.notify(
        title=baslik,
        message=mesaj,
        app_name="Fiyat Takipçisi",
        timeout=5
    )


# 5. Ana Döngü
def main():
    veritabani_hazirla()
    hedef_coin = "bitcoin"  # "ethereum", "solana" vb. yazılabilir
    alarm_esigi = 95000.0  # Örnek bildirim eşiği (USD)

    print(f"[*] {hedef_coin.upper()} takip sistemi başlatıldı...")

    # Test amacıyla döngüyü çalıştırıyoruz (Örn: her 60 saniyede bir kontrol)
    for _ in range(5):
        fiyat = fiyat_getir(hedef_coin)

        if fiyat:
            zaman = datetime.now().strftime("%H:%M:%S")
            print(f"[{zaman}] {hedef_coin.upper()}: ${fiyat}")
            fiyati_kaydet(hedef_coin, fiyat)

            # Eşik kontrolü ve masaüstü bildirimi
            if fiyat >= alarm_esigi:
                bildirim_gonder(
                    f"Fiyat Uyarısı: {hedef_coin.upper()}",
                    f"Güncel Fiyat: ${fiyat}\nBelirlediğin ${alarm_esigi} eşiğini aştı!"
                )

        time.sleep(15)  # 15 saniye bekle


if __name__ == "__main__":
    main()
