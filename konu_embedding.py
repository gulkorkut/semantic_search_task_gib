import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import torch

# .env dosyasını yükle
load_dotenv()

# MongoDB bağlantısı
db_uri = os.getenv("DB_INF")
client = MongoClient(db_uri)
db = client["ozelge_database"]
collection = db["ozelge_collection"]

# GPU kontrolü ve model yüklemesi
device = "cuda" if torch.cuda.is_available() else "cpu"  # GPU varsa kullan
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Embedding'leri dosyaya kaydetme
def save_embeddings_with_konu_to_file():
    # Veritabanından belgeleri çek
    documents = list(collection.find({}, {"_id": 1, "embedding": 1, "konu": 1, "indirme_linki": 1}))
    embeddings = {}

    for doc in documents:
        # Her belgeden embedding ve konu bilgisini al
        embedding = doc.get("embedding", None)
        konu = doc.get("konu", "")

        # Eğer konu varsa, konu embedding'ini oluştur
        if konu:
            konu_embedding = model.encode([konu], convert_to_tensor=True).cpu().detach().numpy()
        else:
            konu_embedding = np.zeros_like(embedding)  # Konu yoksa sıfır vektör kullan

        # Her belgenin embedding'ini ve konu embedding'ini kaydet
        embeddings[str(doc["_id"])] = {
            "embedding": embedding,
            "embedding_konu": konu_embedding,
            "konu": doc.get("konu", ""),
            "indirme_linki": doc.get("indirme_linki", "")
        }

    # Embedding verilerini dosyaya kaydet
    np.save("embedding_cache_konu.npy", embeddings)
    print("Embeddings with Konu saved to embedding_cache_konu.npy")

# Bu fonksiyonu bir defa çalıştırarak verileri kaydedin
save_embeddings_with_konu_to_file()
