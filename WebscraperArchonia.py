import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import random
from datetime import datetime
import json
import time
from dotenv import load_dotenv

# =========================
# WEBHOOK CONFIG (.env)
# =========================
load_dotenv()

WEBHOOK_PROD = os.getenv("DISCORD_WEBHOOK_PROD")
WEBHOOK_TEST = os.getenv("DISCORD_WEBHOOK_TEST")

# True = test webhook
# False = productie webhook
USE_TEST_WEBHOOK = True

WEBHOOK_URL = WEBHOOK_TEST if USE_TEST_WEBHOOK else WEBHOOK_PROD

if not WEBHOOK_URL:
    raise ValueError("❌ Geen webhook gevonden in .env bestand")

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "Archonia_cache.json")
PLACEHOLDER_IMAGE = "https://static.wixstatic.com/media/963c7d_1ba9dcd8f425497f81c3065b1f49652e~mv2.png"
TIMESTAMP = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PAUSE_SECONDS = 1.5

# Sponsors
mdrawz = "https://m-drawz.nl"
SPONSORS = [
    f"[**M-DRAWZ**]({mdrawz})"
]

# Images folder
IMAGES_FOLDER = os.path.join(BASE_DIR, "Images")
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Pagina URLs
BASE_SEARCH_URL = "https://www.archonia.com/nl-be/zoek?page={page}&qf%5B0%5D=3077&qf%5B1%5D=3872&sort=inserted_timestamp_desc"
PAGES = [1, 2, 3, 4, 5]

# =========================
# CACHE FUNCTIES
# =========================
def load_cache():
    try:
        if not os.path.exists(CACHE_FILE):
            return set()
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return set()
            return set(json.loads(content))
    except Exception as e:
        print("⚠️ Cache probleem:", e)
        return set()

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(cache), f, indent=2)
    except Exception as e:
        print("❌ Cache niet opgeslagen:", e)

# =========================
# IMAGE DOWNLOAD
# =========================
def download_image(url, folder=IMAGES_FOLDER):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_name = os.path.basename(url)
            image_path = os.path.join(folder, image_name)
            with open(image_path, "wb") as f:
                f.write(response.content)
            return image_path
        else:
            print(f"⚠️ Kon afbeelding niet downloaden: {url}")
            return None
    except Exception as e:
        print(f"❌ Fout bij downloaden afbeelding: {e}")
        return None

# =========================
# SCRAPER
# =========================
def extract_items(soup):
    items = soup.find_all("div", class_="panel-body p-a-sm")
    print(f"🔎 extract_items(): {len(items)} blocks gevonden")
    return items

def process_items(items, cache):
    new_items = []
    for i, item in enumerate(items, start=1):
        print(f"\n--- ITEM {i} ---")
        try:
            title_tag = item.find("a", attrs={"style": "text-overflow: ellipsis"})
            if not title_tag:
                print("⚠️ Geen title tag, skip")
                continue
            name = title_tag.text.strip()
            link = title_tag.get("href")

            price_tag = item.find("h4", class_="m-y-0")
            price = price_tag.text.strip() if price_tag else "Onbekend"

            img_tag = item.find("img")
            image_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else None
            if not image_url or "image-coming-soon" in image_url:
                image_url = PLACEHOLDER_IMAGE
            elif image_url.startswith("/"):
                image_url = "https://www.archonia.com" + image_url

            status = "Backorder"
            preorder_btn = item.find("button", class_="btn btn-info")
            if preorder_btn:
                status = preorder_btn.find("i").previous_sibling.strip() if preorder_btn.find("i") else "Voorbestelling"
            else:
                buy_btn = item.find("button", class_="btn btn-primary")
                if buy_btn and "Nu kopen" in buy_btn.text:
                    status = "Te koop"

            item_id = link
            if item_id in cache:
                continue

            new_items.append({
                "name": name,
                "price": price,
                "link": "https://www.archonia.com" + link,
                "image_url": image_url,
                "status": status
            })
            cache.add(item_id)

        except Exception as e:
            print("❌ Fout bij verwerken item:", e)

    return new_items

# =========================
# MAIN
# =========================
def main():
    try:
        cache = load_cache()
        print("Cache items:", len(cache))

        all_new_items = []

        for page in PAGES:
            url = BASE_SEARCH_URL.format(page=page)
            response = requests.get(url, headers=HEADERS, timeout=15)
            print(f"\n🌐 Pagina {page} - HTTP status:", response.status_code)
            soup = BeautifulSoup(response.text, "html.parser")
            items = extract_items(soup)
            new_items = process_items(items, cache)
            all_new_items.extend(new_items)

        save_cache(cache)

        print(f"\n🆕 TOTAAL NIEUWE ITEMS GEVONDEN: {len(all_new_items)}\n")

        for item in all_new_items:
            local_image_path = download_image(item["image_url"])
            if not local_image_path:
                local_image_path = os.path.join(IMAGES_FOLDER, os.path.basename(PLACEHOLDER_IMAGE))

            sponsor_text = random.choice(SPONSORS)

            payload = {
                "content": "<:LOGO_Archonia:1416450418619318434> <@&1416441011487506513> Er is een nieuw item op Archonia: <:LOGO_Archonia:1416450418619318434>",
                "embeds": [
                    {
                        "thumbnail": {
                            "url": "https://cdn.discordapp.com/attachments/1247840781218349118/1460724483219394734/LOGO_Archonia.png"
                        },
                        "description": (
                            f'**[{item["name"]}]({item["link"]})**\n'
                            f'Status: {item["status"]}\n'
                            f'Prijs: {item["price"]}\n\n'
                            f'Alerts worden mogelijk gemaakt door {sponsor_text}'
                        ),
                        "image": {"url": f"attachment://{os.path.basename(local_image_path)}"},
                        "footer": {
                            "text": f"Tijdstip van plaatsen bericht: {TIMESTAMP}",
                            "icon_url": "https://m-drawz.nl/wp-content/uploads/2023/01/cropped-M-DRAWZ-Website-logo.png"
                        },
                        "color": 0xF5E727,
                    }
                ]
            }

            with open(local_image_path, "rb") as f:
                files_payload = {"file": f}
                r = requests.post(
                    WEBHOOK_URL,
                    files=files_payload,
                    data={"payload_json": (None, json.dumps(payload))}
                )

            if r.status_code not in (200, 204):
                print("❌ Discord fout:", r.status_code, r.text)
            else:
                print("✅ Verzonden:", item["name"])

            time.sleep(PAUSE_SECONDS)

    except Exception as e:
        print("❌ Fout in main():", e)

if __name__ == "__main__":
    main()