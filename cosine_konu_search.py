import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import time
from pymongo import MongoClient
import os
import torch

# .env dosyasını yükle
from dotenv import load_dotenv
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")
client = MongoClient(db_uri)
db = client["ozelge_database"]
collection = db["ozelge_collection"]

# GPU kontrolü ve model yüklemesi
device = "cuda" if torch.cuda.is_available() else "cpu"  # GPU varsa kullan
print(f"Model {device} üzerinde çalışıyor.")  # Cihaz bilgisini yazdır
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Cache için global değişken
embedding_konu_cache = {}
embedding_konu_file = "files/embedding_konu_cache.npy"

# Kosinüs benzerliği hesaplamak için fonksiyon
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# embedding_konu'leri ve meta verileri dosyaya kaydetme
def save_embedding_konus_to_file():
    documents = list(collection.find({}, {"_id": 1, "embedding_konu": 1, "konu": 1, "indirme_linki": 1}))
    embedding_konus = {
        str(doc["_id"]): {
            "embedding_konu": doc["embedding_konu"],
            "konu": doc.get("konu", ""),
            "indirme_linki": doc.get("indirme_linki", "")
        }
        for doc in documents
    }
    np.save(embedding_konu_file, embedding_konus)

# embedding_konu'leri dosyadan yükleme
def load_embedding_konus_from_file():
    global embedding_konu_cache
    if os.path.exists(embedding_konu_file):
        embedding_konu_cache = np.load(embedding_konu_file, allow_pickle=True).item()
    else:
        save_embedding_konus_to_file()
        embedding_konu_cache = np.load(embedding_konu_file, allow_pickle=True).item()

# Sorgu için fonksiyon
def semantic_search(query, top_n=5):
    query_embedding_konu = model.encode([query], convert_to_tensor=True)
    query_embedding_konu = query_embedding_konu.cpu().detach().numpy()  # GPU'dan çıkarıp numpy dizisine dönüştür

    similarities = []
    for doc_id, data in embedding_konu_cache.items():
        embedding_konu = data["embedding_konu"]
        similarity = cosine_similarity(query_embedding_konu, embedding_konu)
        similarities.append((doc_id, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:top_n]

    results = []
    for doc_id, similarity in top_results:
        data = embedding_konu_cache[doc_id]
        results.append((doc_id, similarity, data["konu"], data["indirme_linki"]))

    return results

# Streamlit UI ve işlevsellik
st.title("Özelge Semantic Search")

# Kullanıcıdan sorgu almak
query = st.text_input("Sorgunuzu girin:", "")

if st.button("Ara"):
    if query:
        #st.write("Sorgu çalıştırılıyor...")
        start_time = time.time()

        # embedding_konu'leri dosyadan yükle veya MongoDB'den çekip kaydet
        load_embedding_konus_from_file()

        # Sorguyu çalıştır
        results = semantic_search(query)

        # Programın çalışma süresi
        end_time = time.time()
        execution_time = end_time - start_time

        #st.write(f"Programın toplam çalışma süresi: {execution_time:.4f} saniye")

        # Sonuçları yazdır
        for result in results:
            doc_id, similarity, konu, indirme_linki = result
            st.write(f"**Özelge:** {konu}")
            st.write(f"**Link:** [{indirme_linki}]({indirme_linki})")
            st.write(f"**Benzerlik Skoru:** {similarity}")
            st.write("-" * 50)
    else:
        st.write("Lütfen bir sorgu girin.")
