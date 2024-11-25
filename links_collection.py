from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time


driver = webdriver.Chrome()

base_url = "https://www.gib.gov.tr"
search_url = f"{base_url}/search/node/kdv%20istisna%20type%3An_ozelge"

# Selenium ile özelge bağlantılarını topla
def fetch_all_links():
    driver.get(search_url)
    time.sleep(3)  

    links = []
    page_count = 0  

    while page_count < 220:  # 220 sayfa olana kadar devam et
        # Sayfadaki tüm bağlantıları XPath sırasına göre bul
        for i in range(1, 11):  # İlk 10 bağlantıyı döngüyle kontrol et
            try:
                xpath = f'//*[@id="block-system-main"]/ol/li[{i}]/h3/a'
                element = driver.find_element(By.XPATH, xpath)
                links.append(element.get_attribute("href"))
            except Exception:
                # Bu sırada bağlantı yoksa atla
                pass

        # Sayfa sayısını artır
        page_count += 1

        # Sonraki sayfa düğmesi
        try:
            next_btn = driver.find_element(By.LINK_TEXT, "sonraki ›")
            ActionChains(driver).move_to_element(next_btn).click().perform()  # Sonraki butonuna tıklama
            time.sleep(3)  # Yeni sayfanın yüklenmesini bekleyin
        except Exception:
            print("Tüm sayfalar tarandı.")
            break

    return links

# Bağlantıları al
links = fetch_all_links()
driver.quit()

# Toplanan bağlantıları yazdır
print(f"Toplam {len(links)} özelge bağlantısı bulundu.")
for link in links:
    print(link)

# Bağlantıları bir dosyaya kaydetmek için
with open("files/ozelge_links.txt", "w", encoding="utf-8") as file:
    for link in links:
        file.write(link + "\n")
