import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import time
from pymongo import MongoClient
import os
import torch
from streamlit.components.v1 import html

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
embedding_cache = {}
embedding_file = "files/embedding_hibrit_cache.npy"

# Kosinüs benzerliği hesaplamak için fonksiyon
def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Eğer normlardan biri sıfırsa NaN döndürme
    if norm_a == 0 or norm_b == 0:
        return float('nan')
    
    return np.dot(a, b) / (norm_a * norm_b)

# Embedding'leri ve meta verileri dosyaya kaydetme
def save_embeddings_to_file():
    documents = list(collection.find({}, {"_id": 1, "embedding": 1,"embedding_konu": 1, "konu": 1, "indirme_linki": 1}))
    embeddings = {
        str(doc["_id"]): {
            "embedding": doc["embedding"],
            "embedding_konu": doc["embedding_konu"],
            "konu": doc.get("konu", ""),
            "indirme_linki": doc.get("indirme_linki", "")
        }
        for doc in documents
    }
    np.save(embedding_file, embeddings)

# Embedding'leri dosyadan yükleme
def load_embeddings_from_file():
    global embedding_cache
    if os.path.exists(embedding_file):
        embedding_cache = np.load(embedding_file, allow_pickle=True).item()
    else:
        save_embeddings_to_file()
        embedding_cache = np.load(embedding_file, allow_pickle=True).item()

# Sorgu için fonksiyon
def semantic_search(query, top_n=5):
    query_embedding = model.encode([query], convert_to_tensor=True)
    query_embedding = query_embedding.cpu().detach().numpy()  # GPU'dan çıkarıp numpy dizisine dönüştür

    query_embedding_konu = model.encode([query], convert_to_tensor=True)  # Konu için de aynı şekilde embedding
    query_embedding_konu = query_embedding_konu.cpu().detach().numpy()

    similarities = []
    for doc_id, data in embedding_cache.items():
        embedding = data["embedding"]
        embedding_konu = data["embedding_konu"]

        similarity = cosine_similarity(query_embedding, embedding)
        topic_similarity = cosine_similarity(query_embedding_konu, embedding_konu)

        # Eğer similarity ya da topic_similarity NaN ise atla
        if np.isnan(similarity) or np.isnan(topic_similarity):
            continue
        
        total_similarity = (similarity + topic_similarity) / 2
        similarities.append((doc_id, similarity, topic_similarity, total_similarity))

    similarities.sort(key=lambda x: x[3], reverse=True)  # total_similarity'ye göre sıralama yapıyoruz
    top_results = similarities[:top_n]

    results = []
    for doc_id, similarity, topic_similarity, total_similarity in top_results:
        data = embedding_cache[doc_id]
        results.append((doc_id, similarity, topic_similarity, total_similarity, data["konu"], data["indirme_linki"]))

    return results

def display_result_as_card(result):
    doc_id, similarity, topic_similarity, total_similarity, konu, indirme_linki = result

    card_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
        <h4 style="margin: 0; color: #0073e6;">{konu}</h4>
        <p style="margin: 5px 0; font-size: 14px;">Toplam Benzerlik Skoru: <strong>{total_similarity:.2f}</strong></p>
        <p style="margin: 5px 0; font-size: 14px;">İçerik Benzerlik Skoru: {similarity:.2f}</p>
        <p style="margin: 5px 0; font-size: 14px;">Konu Benzerlik Skoru: {topic_similarity:.2f}</p>
        <a href="{indirme_linki}" style="text-decoration: none; color: #ffffff; background-color: #0073e6; padding: 10px 15px; border-radius: 5px; font-size: 14px;">İndirme Linki</a>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Streamlit UI ve işlevsellik
st.title("Özelge Semantic Search")

# Kullanıcıdan sorgu almak
query = st.text_input("Sorgunuzu girin:", "")

if st.button("Ara"):
    if query:
        st.info("Arama işlemi başlatıldı...")
        start_time = time.time()

        load_embeddings_from_file()
        results = semantic_search(query)

        end_time = time.time()
        execution_time = end_time - start_time
        st.success(f"Arama tamamlandı! Süre: {execution_time:.2f} saniye.")

        if results:
            for result in results:
                display_result_as_card(result)
        else:
            st.warning("Sonuç bulunamadı.")
    else:
        st.error("Lütfen bir sorgu girin.")

