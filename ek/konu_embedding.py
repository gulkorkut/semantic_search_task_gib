from sentence_transformers import SentenceTransformer
import numpy as np
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")
client = MongoClient(db_uri)
db = client["ozelge_database"]
collection = db["ozelge_collection"]

# SBERT modelini yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

def save_embeddings_to_file():
    """
    'embedding', 'konu' ve 'indirme_linki' bilgilerini içeren embeddings'i hesaplayıp,
    npy formatında kaydeder.
    """
    # MongoDB'den tüm içerikleri al
    documents = list(collection.find({}, {"_id": 1, "embedding": 1, "konu": 1, "indirme_linki": 1}))  
    konu_contents = [doc["konu"] for doc in documents]

    # SBERT ile içerik ve konu embedding'lerini hesapla
    print("Embedding'ler hesaplanıyor...")
    konu_embeddings = model.encode(konu_contents).tolist()

    # Embedding ve ek bilgileri birleştir
    embeddings_data = {
        str(doc["_id"]): {
            "embedding": doc["embedding"],
            "konu_embedding": konu_embeddings[i],
            "konu": doc.get("konu", ""),
            "indirme_linki": doc.get("indirme_linki", "")
        }
        for i, doc in enumerate(documents)
    }

    # Embedding'leri .npy dosyasına kaydet
    np.save("embeddings_with_konu.npy", embeddings_data)

    print("Tüm embedding'ler başarıyla kaydedildi.")

# Fonksiyonu çalıştır
save_embeddings_to_file()
