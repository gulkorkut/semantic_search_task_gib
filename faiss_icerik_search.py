import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import time
from pymongo import MongoClient
import os
import torch
import faiss

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

# FAISS index ve metadata cache
faiss_index = None
metadata_cache = {}

# Embedding'leri MongoDB'den çekip FAISS index oluşturma
def build_faiss_index():
    global faiss_index, metadata_cache

    # Verileri MongoDB'den çek
    documents = list(collection.find({}, {"_id": 1, "embedding": 1, "konu": 1, "indirme_linki": 1}))
    
    # Embedding'leri ve metadata'yı ayır
    embeddings = []
    metadata_cache = {}
    for i, doc in enumerate(documents):
        embeddings.append(doc["embedding"])
        metadata_cache[i] = {
            "_id": str(doc["_id"]),
            "konu": doc.get("konu", ""),
            "indirme_linki": doc.get("indirme_linki", "")
        }

    # FAISS index oluştur
    embedding_dim = len(embeddings[0])  # Embedding boyutu
    faiss_index = faiss.IndexFlatL2(embedding_dim)  # L2 norm kullanan index
    faiss_index.add(np.array(embeddings).astype("float32"))  # FAISS float32 türü gerektirir

# FAISS ile benzerlik araması
def semantic_search_faiss(query, top_n=5):
    global faiss_index, metadata_cache

    # Sorguyu encode et
    query_embedding = model.encode([query], convert_to_tensor=True).cpu().numpy()

    # FAISS ile en yakın komşuları bul
    distances, indices = faiss_index.search(query_embedding.astype("float32"), top_n)

    # Sonuçları metadata ile birleştir
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        metadata = metadata_cache[idx]
        results.append({
            "distance": dist,
            "konu": metadata["konu"],
            "indirme_linki": metadata["indirme_linki"]
        })
    return results

# Streamlit UI ve işlevsellik
st.title("Özelge Semantic Search")

# Kullanıcıdan sorgu almak
query = st.text_input("Sorgunuzu girin:", "")

if st.button("Ara"):
    if query:
        # FAISS index'i oluştur (ilk çalıştırmada yapılır)
        if faiss_index is None:
            build_faiss_index()

        # Sorguyu çalıştır
        start_time = time.time()
        results = semantic_search_faiss(query)
        end_time = time.time()

        # Programın çalışma süresi
        execution_time = end_time - start_time
        st.write(f"Arama süresi: {execution_time:.4f} saniye")

        # Sonuçları yazdır
        for result in results:
            st.write(f"**Özelge:** {result['konu']}")
            st.write(f"**Link:** [{result['indirme_linki']}]({result['indirme_linki']})")
            st.write(f"**Benzerlik Skoru:** {1 - result['distance']:.4f}")  # Skor tersine çevrildi, çünkü FAISS mesafeleri döndürüyor
            st.write("-" * 50)
    else:
        st.write("Lütfen bir sorgu girin.")
