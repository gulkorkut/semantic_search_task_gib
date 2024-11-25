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
    Tüm embedding'leri bir seferde hesaplar, hem veritabanına hem de bir dosyaya kaydeder. Daha hızlı işlem amaçlandı.
    """
    # MongoDB'den tüm içerikleri al
    documents = list(collection.find({}, {"_id": 1, "icerik": 1}))  # '_id' ve 'icerik' alanlarını al
    contents = [doc["icerik"] for doc in documents]

    # SBERT ile embedding'leri hesapla
    print("Embedding hesaplanıyor...")
    embeddings = model.encode(contents).tolist()

    # Bellekte tüm veriyi tutmak için liste oluştur
    embeddings_data = []

    # Embedding'leri veritabanına kaydet ve aynı zamanda bellekte tut
    for i, doc in enumerate(documents):
        # Veritabanına embedding'i kaydet. Update one ile tek tek değil de bir kerede güncelleme.
        collection.update_one({"_id": doc["_id"]}, {"$set": {"embedding": embeddings[i]}})
        
        # Bellekte tut
        embeddings_data.append({"_id": str(doc["_id"]), "embedding": embeddings[i]})
        
        print(f"Embedding kaydedildi: {doc['_id']}")

    # Bellekteki veriyi dosyaya yaz
    with open("files/embeddings/embeddings.jsonl", "w", encoding="utf-8") as file:
        for data in embeddings_data:
            json.dump(data, file)
            file.write("\n")

    print("Tüm embedding'ler başarıyla kaydedildi.")

# Fonksiyonu çalıştır
store_embeddings_bulk()
