from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time
from variables import *

# .env dosyasını yükle
load_dotenv()

db_uri = os.getenv("DB_INF")  # MongoDB bağlantı URI'sini .env'den al
client = MongoClient(db_uri)  
db = client["ozelge_database"]  
collection = db["ozelge_collection"]  

# İlk defa indexleme yapılırken burayı kullan
# 'id' alanı için unique index oluşturuluyor
# collection.create_index([("id", 1)], unique=True)


driver = webdriver.Chrome()

# Bağlantı dosyası
input_file = "files/ozelge_links.txt"

def fetch_ozelge_content(link):
    """Bir linke giderek içerik çeker ve MongoDB'ye gönderir."""
    driver.get(link)  
    time.sleep(3)  

    data_to_insert = []

    try:
        content_element = driver.find_element(By.XPATH, CONTENT_XPATH)
        content = content_element.text.strip()

        id_element = driver.find_element(By.XPATH, ID_XPATH)
        id_text = id_element.text.strip().replace("Sayı :", "").strip()

        subject_element = driver.find_element(By.XPATH, SUBJECT_XPATH)
        subject_text = subject_element.text.replace("Konu :", "").strip()

        try:
            date_element = driver.find_element(By.XPATH, DATE_XPATH)
            ozelge_tarihi = date_element.text.strip()
        except Exception:
            ozelge_tarihi = None

        try:
            download_element = driver.find_element(By.XPATH, DOWNLOAD_XPATH)
            download_link = download_element.get_attribute("href")
            if not download_link.startswith("http"):
                download_link = BASE_URL + download_link
        except Exception:
            download_link = None

        data = {
            "id": id_text,
            "konu": subject_text,
            "ozelge_linki": link,
            "ozelge_tarihi": ozelge_tarihi,
            "indirme_linki": download_link,
            "icerik": content
        }

        data_to_insert.append(data)

    except Exception as e:
        print(f"{link} adresinde hata oluştu: {e}")

    # Toplu ekleme işlemi, aynı id varsa eklenmez
    if data_to_insert:
        try:
            collection.insert_many(data_to_insert, ordered=False)  # Aynı id varsa eklenmez
            #print(f"{len(data_to_insert)} yeni veri eklendi.")
        except Exception as e:
            print(f"Veri eklenirken hata oluştu: {e}")

# Bağlantı dosyasını oku
with open(input_file, "r", encoding="utf-8") as file:
    links = file.readlines()

# Linkleri işle
for link in links:
    link = link.strip()  # Satırdaki gereksiz boşlukları temizle
    if not link:  # Eğer satır boşsa atla
        continue

    # İçeriği çek ve MongoDB'ye kaydet
    fetch_ozelge_content(link)

driver.quit()

print("Tüm içerikler MongoDB'ye gönderildi.")
