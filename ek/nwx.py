from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time
from variables import *
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")  # MongoDB bağlantı URI'sini .env'den al
client = MongoClient(db_uri)  # MongoDB istemcisini oluştur
db = client["ozelge_database"]  # Veritabanı adı
collection = db["ozelge_collection"]  # Koleksiyon adı

# ChromeDriver yolunu belirtin
driver_path = "path/to/chromedriver"
driver = webdriver.Chrome()


# Giriş bağlantı dosyasını tanımlayın
input_file = "ozelge_links_short.txt"

def fetch_ozelge_content(link):
    """Bir linke giderek içerik çeker ve MongoDB'ye gönderir."""
    driver.get(link)  # Sayfaya git
    time.sleep(3)  # Sayfanın yüklenmesini bekle
    
    try:
        # XPath ile içeriği bul
        content_element = driver.find_element(By.XPATH, CONTENT_XPATH)
        content = content_element.text.strip()  # İçeriği al ve temizle

        # ID'yi bul
        id_element = driver.find_element(By.XPATH, ID_XPATH)
        id_text = id_element.text.strip().replace("Sayı :", "").strip()

        # Konuyu bul
        subject_element = driver.find_element(By.XPATH, SUBJECT_XPATH)
        subject_text = subject_element.text.replace("Konu :", "").strip()

        # Tarihi bul
        try:
            date_element = driver.find_element(By.XPATH, DATE_XPATH)
            ozelge_tarihi = date_element.text.strip()
        except Exception:
            ozelge_tarihi = None

        # İndirme bağlantısını bul
        try:
            download_element = driver.find_element(By.XPATH, DOWNLOAD_XPATH)
            download_link = download_element.get_attribute("href")  # İndirme linkini al
            # Bağlantının tam URL olmasını sağla
            if not download_link.startswith("http"):
                download_link = BASE_URL + download_link
        except Exception:
            download_link = None  # Eğer indirme linki bulunamazsa None ata

        # MongoDB için veri hazırlama
        data = {
            "id": id_text,
            "konu": subject_text,
            "ozelge_linki": link,  # Orijinal linki tut
            "ozelge_tarihi": ozelge_tarihi,
            "indirme_linki": download_link,  # İndirme linki
            "icerik": content
        }

        # MongoDB'ye gönder
        collection.insert_one(data)
       # print(f"Veri eklendi: {data}")
    except Exception as e:
        print(f"{link} adresinde hata oluştu: {e}")

# Bağlantı dosyasını okuyun
with open(input_file, "r", encoding="utf-8") as file:
    links = file.readlines()

# Linkleri işleyin
for link in links:
    link = link.strip()  # Satırdaki gereksiz boşlukları temizle
    if not link:  # Eğer satır boşsa atla
        continue

    # İçeriği çek ve MongoDB'ye kaydet
    fetch_ozelge_content(link)

# Tarayıcıyı kapat
driver.quit()

print("Tüm içerikler MongoDB'ye gönderildi.")
