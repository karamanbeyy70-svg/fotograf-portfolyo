import os
import requests
from bs4 import BeautifulSoup

# Çevre değişkenlerinden Instagram bilgilerini al
ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")

def get_latest_instagram_post():
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}/media?fields=id,caption,media_type,media_url,permalink,timestamp&access_token={ACCESS_TOKEN}"
    response = requests.get(url).json()
    
    if "data" in response and len(response["data"]) > 0:
        # En son paylaşılan gönderiyi al (Görsel veya Carousel)
        for post in response["data"]:
            if post.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"]:
                return post
    return None

def update_portfolio():
    post = get_latest_instagram_post()
    if not post:
        print("Yeni görsel bulunamadı.")
        return

    post_id = post["id"]
    media_url = post["media_url"]
    caption = post.get("caption", "Yeni Fotoğraf")
    image_filename = f"instagram_{post_id}.jpg"
    image_path = os.path.join("images", image_filename)

    # Görsel daha önce indirilmiş mi kontrol et
    if os.path.exists(image_path):
        print("Bu gönderi zaten portfolyoya eklenmiş.")
        return

    # Görseli images/ klasörüne kaydet
    os.makedirs("images", exist_ok=True)
    img_data = requests.get(media_url).content
    with open(image_path, "wb") as f:
        f.write(img_data)
    print(f"Görsel kaydedildi: {image_path}")

    # Açıklamadan kategori tahmin et
    category = "birds"
    caption_lower = caption.lower()
    if "uzun pozlama" in caption_lower or "nd filter" in caption_lower:
        category = "long-exposure"
    elif "havacılık" in caption_lower or "uçak" in caption_lower or "spotter" in caption_lower:
        category = "aviation"
    elif "astro" in caption_lower or "samanyolu" in caption_lower or "dolunay" in caption_lower:
        category = "astro"

    # HTML Kartını Oluştur
    new_card = f"""
            <!-- Otomatik Instagram Gönderisi -->
            <div class="gallery-item group relative cursor-pointer overflow-hidden aspect-[4/5]" 
                 data-category="{category}" 
                 data-title="{caption[:30]}..." 
                 data-location="Instagram Gönderisi"
                 data-body="-" 
                 data-lens="-" 
                 data-f="-" 
                 data-iso="-" 
                 data-shutter="-">
                <img src="{image_path}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" alt="{caption[:30]}">
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center p-4 text-center">
                    <span class="text-white tracking-widest uppercase text-sm mb-1">Görüntüle</span>
                    <span class="text-zinc-300 text-xs flex items-center gap-1"><i class="fa-solid fa-camera"></i> Instagram</span>
                </div>
            </div>
"""

    # index.html dosyasını güncelle
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    grid_marker = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" id="gallery-grid">'
    if grid_marker in html_content:
        updated_html = html_content.replace(grid_marker, grid_marker + "\n" + new_card)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_html)
        print("index.html başarıyla güncellendi.")

if __name__ == "__main__":
    update_portfolio()
