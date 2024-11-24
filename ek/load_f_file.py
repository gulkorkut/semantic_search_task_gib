from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from bson import ObjectId  # ObjectId sınıfını içe aktardık
import os
import numpy as np
from dotenv import load_dotenv
import time

# .env dosyasını yükle
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")
client = MongoClient(db_uri)
db = client["ozelge_database"]
collection = db["ozelge_collection"]

# SBERT modelini yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

# Cache için global değişken
embedding_cache = {}
embedding_file = "embedding_cache.npy"

# Kosinüs benzerliği hesaplamak için fonksiyon
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Embedding'leri dosyaya kaydetme
def save_embeddings_to_file():
    """
    MongoDB'deki embedding'leri ve belgelerin ID'lerini bir dosyaya kaydeder.
    """
    documents = list(collection.find({}, {"_id": 1, "embedding": 1}))
    embeddings = {str(doc["_id"]): doc["embedding"] for doc in documents}
    np.save(embedding_file, embeddings)
    print(f"Embedding'ler {embedding_file} dosyasına kaydedildi.")

# Embedding'leri dosyadan yükleme
def load_embeddings_from_file():
    """
    Embedding'leri bir dosyadan yükler.
    """
    global embedding_cache
    if os.path.exists(embedding_file):
        embedding_cache = np.load(embedding_file, allow_pickle=True).item()
        print(f"Embedding'ler {embedding_file} dosyasından yüklendi.")
    else:
        print(f"Embedding dosyası bulunamadı. MongoDB'den çekiliyor.")
        save_embeddings_to_file()
        embedding_cache = np.load(embedding_file, allow_pickle=True).item()

# Sorgu için fonksiyon
def semantic_search(query, top_n=5):
    """
    Kullanıcı sorgusuna en benzer belgeleri arar.
    """
    # Kullanıcı sorgusunu embedding'e dönüştür
    query_embedding = model.encode([query])[0]

    similarities = []
    for doc_id, embedding in embedding_cache.items():
        # Embedding ile kullanıcı sorgusunun benzerliğini hesapla
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((doc_id, similarity))

    # En benzer N belgeyi sırala
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:top_n]

    # Ek bilgileri (konu ve indirme linki) veritabanından çek
    results = []
    for doc_id, similarity in top_results:
        try:
            document = collection.find_one({"_id": ObjectId(doc_id)}, {"konu": 1, "indirme_linki": 1})
        except Exception as e:
            print(f"Error fetching document with ID {doc_id}: {e}")
            document = None

        if document:
            results.append((doc_id, similarity, document.get("konu", ""), document.get("indirme_linki", "")))
        else:
            print(f"Warning: Document with ID {doc_id} not found.")
            results.append((doc_id, similarity, "Bilinmiyor", "Bilinmiyor"))

    return results

# Kullanıcı sorgusunu al
query = "Stok beyanı hakkında ödeme yapılması gerektiği durumu anlatan özelge"

# Programın çalışma süresi
start_time = time.time()  # Zaman ölçümünü başlat

# Embedding'leri dosyadan yükle veya MongoDB'den çekip kaydet
load_embeddings_from_file()

# Sorguyu çalıştır
results = semantic_search(query)

# Programın çalışma süresi
end_time = time.time()  # Zaman ölçümünü bitir
execution_time = end_time - start_time  # Toplam çalışma süresi

# Sonuçları yazdır
for result in results:
    doc_id, similarity, konu, indirme_linki = result
    print(f"Link: {indirme_linki}")
    print(f"ID: {doc_id}, Konu: {konu}")
    print(f"Benzerlik Skoru: {similarity}")
    print("-" * 50)

# Toplam çalışma süresini yazdır
print(f"Programın toplam çalışma süresi: {execution_time:.4f} saniye")


#Bu 5 sorgu hala veritabanından