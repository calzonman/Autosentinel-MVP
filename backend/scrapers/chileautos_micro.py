import re
import urllib.parse
import asyncio
import numpy as np
from playwright.sync_api import sync_playwright

def get_chileautos_market_median_sync(brand: str, model: str, year: int = None) -> dict:
    """
    Micro-scraper sincrónico de Chileautos diseñado para ejecutarse de forma segura
    en hilos secundarios en Windows sin conflictos de redirección o Event Loop.
    
    URL objetivo: https://www.chileautos.cl/vehiculos/?q=CarAll.keyword({brand} {model} {year}).
    """
    clean_brand = brand.strip() if brand else ""
    clean_model = model.strip() if model else ""
    clean_year = str(year).strip() if year else ""

    # Si la marca enviada es un año de 4 dígitos (ej: "2019"), corregir posición
    if clean_brand.isdigit() and len(clean_brand) == 4:
        clean_year = clean_brand
        model_parts = clean_model.split(" ")
        clean_brand = model_parts[0] if model_parts else ""
        clean_model = " ".join(model_parts[1:]) if len(model_parts) > 1 else ""

    terms = [clean_brand, clean_model]
    if clean_year:
        terms.append(clean_year)
    search_term = " ".join([t for t in terms if t])

    # Construir URL usando %20 para espacios en blanco (sin utilizar '+')
    encoded_search = search_term.replace(" ", "%20")
    url = f"https://www.chileautos.cl/vehiculos/?q=CarAll.keyword%28{encoded_search}%29."
    
    print(f"[Chileautos Micro-Scraper] Consultando URL: {url}")
    extracted_prices = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="es-CL"
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=35000, wait_until="domcontentloaded")
                
                # Esperar a que la navegación o ticket de redirección se estabilice
                try:
                    page.wait_for_load_state("networkidle", timeout=6000)
                except Exception:
                    page.wait_for_timeout(3000)

                try:
                    page.wait_for_selector('a[href*="/vehiculos/detalles/"]', timeout=8000)
                except Exception:
                    page.wait_for_timeout(2000)

                # Scroll protegido contra cambios de contexto
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    page.wait_for_timeout(1500)
                except Exception:
                    pass

                # Buscar enlaces de detalles de cada publicación (/vehiculos/detalles/...)
                detail_links = page.query_selector_all('a[href*="/vehiculos/detalles/"]')
                seen_urls = set()

                for link in detail_links:
                    try:
                        href = link.get_attribute("href")
                        if not href or href in seen_urls:
                            continue
                        seen_urls.add(href)

                        # Encontrar el contenedor de la tarjeta
                        card_container = link.evaluate_handle("el => el.closest('div._1lalutr170') || el.closest('div.iompba0') || el.parentElement")
                        if not card_container:
                            continue

                        card_text = card_container.evaluate("el => el.innerText")
                        if not card_text:
                            continue

                        # Buscar precio en formato $5,000,000 o $5.000.000 en la tarjeta
                        price_match = re.search(r"\$\s*([0-9]{1,3}(?:[.,][0-9]{3})+)", card_text)
                        if price_match:
                            price_str = price_match.group(1).replace(".", "").replace(",", "")
                            price_val = int(price_str)
                            if 500000 <= price_val <= 90000000:
                                extracted_prices.append(price_val)

                    except Exception:
                        continue

            except Exception as page_err:
                print(f"[Chileautos Page Error] {page_err}")
            finally:
                browser.close()

    except Exception as sys_err:
        print(f"[Chileautos System Error] {sys_err}")

    if not extracted_prices:
        return {
            "success": False,
            "sample_count": 0,
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "prices": [],
            "message": f"No se encontraron publicaciones activas en Chileautos para '{search_term}'"
        }

    # Calcular mediana, promedio y rango estadístico
    prices_arr = np.array(extracted_prices)
    median_val = int(round(float(np.median(prices_arr))))
    min_val = int(np.min(prices_arr))
    max_val = int(np.max(prices_arr))
    avg_val = int(round(float(np.mean(prices_arr))))

    print(f"[Chileautos Micro-Scraper] Mediana calculada: ${median_val:,} de {len(extracted_prices)} publicaciones reales")

    return {
        "success": True,
        "sample_count": len(extracted_prices),
        "median_price": median_val,
        "min_price": min_val,
        "max_price": max_val,
        "avg_price": avg_val,
        "prices": extracted_prices,
        "message": f"Mediana calculada exitosamente (${median_val:,}) sobre {len(extracted_prices)} publicaciones en Chileautos"
    }

async def get_chileautos_market_median(brand: str, model: str, year: int = None) -> dict:
    """Wrapper asíncrono que ejecuta la función sincrónica en un hilo dedicado"""
    return await asyncio.to_thread(get_chileautos_market_median_sync, brand, model, year)

if __name__ == "__main__":
    res = asyncio.run(get_chileautos_market_median("jac", "s2", 2019))
    print(res)
