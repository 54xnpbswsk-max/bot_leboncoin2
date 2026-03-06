import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Telegram ---
TOKEN = os.environ["TOKEN"]
CHAT_IDS = os.environ["CHAT_IDS"].split(",")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        requests.post(url, data={"chat_id": chat_id, "text": msg})

# --- Mémoire des annonces déjà envoyées ---
SEEN_FILE = "seen_ads.txt"
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(line.strip() for line in f)
else:
    seen = set()

# --- Selenium ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- URL Leboncoin (mets ton lien avec tes filtres ici) ---
URL = "https://www.leboncoin.fr/recherche?category=2&price=min-2000&mileage=min-200000&u_car_brand=AUDI,BMW,CITROEN,FORD,OPEL,PEUGEOT,RENAULT,VOLKSWAGEN,ALFA%20ROMEO,HONDA,HYUNDAI,KIA,NISSAN,TOYOTA&u_car_model=AUDI_A3,BMW_S%C3%A9rie%201,CITROEN_C1,CITROEN_C2,CITROEN_C3,OPEL_Corsa,PEUGEOT_107,PEUGEOT_207,PEUGEOT_206,PEUGEOT_307,PEUGEOT_306,PEUGEOT_308,RENAULT_Clio,RENAULT_Megane,RENAULT_Twingo,VOLKSWAGEN_Golf,VOLKSWAGEN_Polo&sort=time&order=desc"

# --- Boucle principale ---
while True:
    driver.get(URL)
    time.sleep(3)  # laisser la page charger

    ads = driver.find_elements(By.CSS_SELECTOR, "a[data-qa-id='aditem_container']")
    for ad in ads:
        link = ad.get_attribute("href")
        title = ad.get_attribute("aria-label") or "Nouvelle annonce"
        if link not in seen:
            send(f"🚗 {title}\n{link}")
            seen.add(link)

    # sauvegarde des annonces déjà envoyées
    with open(SEEN_FILE, "w") as f:
        for l in seen:
            f.write(l + "\n")

    time.sleep(30)  # vérification toutes les 30s
