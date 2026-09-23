import urllib.parse
import re
import numpy as np
from playwright.sync_api import sync_playwright

def scrape_chileautos_exact(brand: str, model: str, year: int = None) -> dict:
    clean_brand = brand.strip() if brand else ""
    clean_model = model.strip() if model else ""
    clean_year = str(year).strip() if year else ""

    terms = [clean_brand, clean_model]
    if clean_year:
        terms.append(clean_year)
    search_term = " ".join([t for t in terms if t])

    encoded_search = search_term.replace(" ", "%20")
    url = f"https://www.chileautos.cl/vehiculos/?q=CarAll.keyword%28{encoded_search}%29."
    
    print(f"[Chileautos Micro-Scraper] URL: {url}")
    extracted_prices = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="es-CL"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=35000)
            page.wait_for_timeout(4000)
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(2000)

            detail_links = page.query_selector_all('a[href*="/vehiculos/detalles/"]')
            print(f"  -> Enlaces de detalles encontrados en DOM: {len(detail_links)}")

            seen_urls = set()
            for link in detail_links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    card_container = link.evaluate_handle("el => el.closest('div._1lalutr170') || el.closest('div.iompba0') || el.parentElement")
                    if not card_container:
                        continue

                    card_text = card_container.evaluate("el => el.innerText")
                    if not card_text:
                        continue

                    price_match = re.search(r"\$\s*([0-9]{1,3}(?:[.,][0-9]{3})+)", card_text)
                    if price_match:
                        price_str = price_match.group(1).replace(".", "").replace(",", "")
                        price_val = int(price_str)
                        if 500000 <= price_val <= 90000000:
                            extracted_prices.append(price_val)
                            print(f"     [Resultado #{len(extracted_prices)}] ${price_val:,} - {href}")

                except Exception as card_err:
                    continue

        except Exception as e:
            print(f"[Chileautos Micro-Scraper Error] {e}")
        finally:
            browser.close()

    print(f"  -> Total Publicaciones Reales Extraídas: {len(extracted_prices)}")
    if extracted_prices:
        prices_arr = np.array(extracted_prices)
        median_val = int(round(float(np.median(prices_arr))))
        min_val = int(np.min(prices_arr))
        max_val = int(np.max(prices_arr))
        print(f"  -> Mediana Calculada: ${median_val:,} (Rango: ${min_val:,} - ${max_val:,})")
        return {
            "success": True,
            "sample_count": len(extracted_prices),
            "median_price": median_val,
            "min_price": min_val,
            "max_price": max_val,
            "prices": extracted_prices,
            "message": f"Mediana calculada exitosamente (${median_val:,}) sobre {len(extracted_prices)} publicaciones en Chileautos"
        }
    else:
        return {
            "success": False,
            "sample_count": 0,
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "prices": [],
            "message": f"No se encontraron publicaciones activas en Chileautos para '{search_term}'"
        }

if __name__ == "__main__":
    print("\n==========================================")
    print("TEST 1: Chevrolet Spark 2019")
    print("==========================================")
    scrape_chileautos_exact("chevrolet", "spark", 2019)

    print("\n==========================================")
    print("TEST 2: Honda HR-V 2017")
    print("==========================================")
    scrape_chileautos_exact("honda", "hr-v", 2017)
