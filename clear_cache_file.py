# Cache için global değişken
embedding_cache = {}

# Cache'i temizleme fonksiyonu (Bir kez çalıştırılacak)
def clear_cache():
    """Cache'i temizler."""
    global embedding_cache
    embedding_cache = {}  # Cache'i sıfırla

# Cache'in temizlenip temizlenmediğini kontrol etme fonksiyonu
def check_cache():
    if len(embedding_cache) == 0:
        print("Cache boş, temizlendi.")
    else:
        print(f"Cache'te {len(embedding_cache)} öğe var.")

# Cache'i temizle
clear_cache()
# Cache'i kontrol et
check_cache()

# Cache'in başarıyla temizlendiği mesajını yazdır
print("Cache başarıyla temizlendi.")
