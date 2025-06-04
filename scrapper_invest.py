from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import datetime

def obtener_empresas_ayer():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--lang=es-ES')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://es.investing.com/earnings-calendar/")

    time.sleep(5)

    # Aceptar cookies si aparecen
    try:
        btn_config = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        btn_config.click()
        time.sleep(2)
    except Exception as e:
        print("⚠️ No se mostró o falló aceptar cookies:", e)

    # Pulsar "Ayer"
    try:
        btn_ayer = driver.find_element(By.XPATH, "//a[contains(text(), 'Ayer')]")
        btn_ayer.click()
        time.sleep(5)
    except Exception as e:
        print("❌ No se pudo hacer clic en 'Ayer':", e)

    # Capturar HTML y cerrar navegador
    html = driver.page_source
    driver.quit()

    # Parsear con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    tickers = []

    for link in soup.find_all("a", class_="bold middle"):
        ticker = link.text.strip()
        if ticker:
            tickers.append(ticker)

    print(f"✅ Se encontraron {len(tickers)} tickers que reportaron ayer.")
    return tickers

# Ejecución de ejemplo
if __name__ == "__main__":
    empresas = obtener_empresas_ayer()

    # Calcular fecha de ayer
    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Crear carpeta si no existe
    os.makedirs("data", exist_ok=True)

    # Guardar en archivo con nombre por fecha
    ruta = f"data/tickers_{ayer}.csv"
    pd.DataFrame(empresas, columns=["Ticker"]).to_csv(ruta, index=False)

    print(f"📁 Guardado en: {ruta}")
    print(empresas[:10])
