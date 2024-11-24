from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json

# .env dosyasını yükle
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")
client = MongoClient(db_uri)
db = client["ozelge_database"]
collection = db["ozelge_collection"]

# SBERT modelini yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

def store_embeddings_bulk():
    """
    Tüm embedding'leri bir seferde hesaplar, hem veritabanına hem de bir dosyaya kaydeder.
    """
    # MongoDB'den tüm içerikleri al
    documents = list(collection.find({}, {"_id": 1, "konu": 1}))  # '_id' ve 'konu' alanlarını al
    konu = [doc["konu"] for doc in documents]

    # SBERT ile embedding'leri hesapla
    print("Embedding hesaplanıyor...")
    embeddings_konu = model.encode(konu).tolist()

    # Bellekte tüm veriyi tutmak için liste oluştur
    embeddings_konu_data = []

    # Embedding'leri veritabanına kaydet ve aynı zamanda bellekte tut
    for i, doc in enumerate(documents):
        # Veritabanına embedding'i kaydet
        collection.update_one({"_id": doc["_id"]}, {"$set": {"embedding_konu": embeddings_konu[i]}})
        
        # Bellekte tut
        embeddings_konu_data.append({"_id": str(doc["_id"]), "embedding_konu": embeddings_konu[i]})
        
        # Süreç bilgisi
        print(f"Embedding kaydedildi: {doc['_id']}")

    # Bellekteki veriyi dosyaya yaz
    with open("embeddings_konu.jsonl", "w", encoding="utf-8") as file:
        for data in embeddings_konu_data:
            json.dump(data, file)
            file.write("\n")

    print("Tüm embedding'ler başarıyla kaydedildi.")

# Fonksiyonu çalıştır
store_embeddings_bulk()
