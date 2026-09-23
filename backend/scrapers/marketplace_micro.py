import os
import sys
import re
import urllib.parse
import asyncio
import numpy as np
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.auth_helper import AUTH_FILE

BADGE_TAGS = {
    "recién publicado", "recien publicado", "recién agregados", "recien agregados",
    "nuevo", "novedad", "patrocinado", "publicación patrocinada", "envío gratis", "envio gratis",
    "destacado", "oferta", "artículo nuevo", "articulo nuevo"
}

def extract_clean_title(lines: list[str], price: int = 0) -> str:
    """
    Filtra insignias de estado, precios y metadatos de las tarjetas de Marketplace
    para extraer la cadena correspondiente al título real del vehículo.
    
    @param lines: Lista de líneas de texto extraídas de la tarjeta de Marketplace.
    @param price: Precio detectado de la publicación para descarte numérico.
    @return: Título limpio del vehículo.
    """
    for line in lines:
        clean = line.strip()
        clean_lower = clean.lower()

        if clean_lower in BADGE_TAGS:
            continue
        if clean.startswith("$") or (price > 0 and clean.replace(".", "").replace("$", "").strip().isdigit()):
            continue
        if clean_lower.startswith("hace ") and any(unit in clean_lower for unit in ["hora", "día", "dia", "minuto"]):
            continue

        return clean

    return lines[0] if lines else "Vehículo sin título"

def get_marketplace_market_median_sync(brand: str, model: str, year: int = None, max_results: int = 100) -> dict:
    """
    Micro-scraper sincrónico de Facebook Marketplace para validación de precios de mercado.
    Especialmente diseñado para ejecutarse con navegador visible (headless=False) en hilos dedicados.
    
    Toma hasta 100 resultados iniciales y filtra ESTRICTAMENTE aquellos que contengan las palabras
    específicas del auto en el título (ej: 'chevrolet spark 2016').
    """
    clean_brand = brand.strip() if brand else ""
    clean_model = model.strip() if model else ""
    clean_year = str(year).strip() if year else ""

    # Normalizar marca / año si vinieron invertidos
    if clean_brand.isdigit() and len(clean_brand) == 4:
        clean_year = clean_brand
        parts = clean_model.split(" ")
        clean_brand = parts[0] if parts else ""
        clean_model = " ".join(parts[1:]) if len(parts) > 1 else ""

    search_terms = [t for t in [clean_brand, clean_model, clean_year] if t]
    search_query_str = " ".join(search_terms)

    # Tokens requeridos para filtro estricto por nombre
    required_tokens = [tok.lower() for tok in search_query_str.split()]

    encoded_query = urllib.parse.quote(search_query_str)
    url = f"https://www.facebook.com/marketplace/106039289436408/search?query={encoded_query}"

    print(f"[Marketplace Validation Scraper] Búsqueda: '{search_query_str}' -> URL: {url}")
    print(f"[Marketplace Validation Scraper] Tokens requeridos para filtro estricto: {required_tokens}")

    auth_path = os.path.abspath(AUTH_FILE)
    use_auth = os.path.exists(auth_path) and os.path.getsize(auth_path) > 50

    extracted_prices = []
    matching_titles = []
    seen_ids = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-notifications",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )

            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "viewport": {"width": 1366, "height": 768},
                "locale": "es-CL"
            }
            if use_auth:
                context_kwargs["storage_state"] = auth_path
                print(f"[Marketplace Validation] Reutilizando sesión autenticada: {auth_path}")

            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            page.goto(url, timeout=35000, wait_until="domcontentloaded")
            page.wait_for_timeout(3500)

            scroll_attempts = 0
            max_scroll_attempts = 15

            while scroll_attempts < max_scroll_attempts:
                scroll_attempts += 1

                links = page.query_selector_all("a[href*='/marketplace/item/']")
                print(f"[Marketplace Validation Scroll {scroll_attempts}] Enlaces en DOM: {len(links)} (Total escaneados: {len(seen_ids)})")

                for link_elem in links:
                    if len(seen_ids) >= max_results:
                        break

                    try:
                        href = link_elem.get_attribute("href")
                        if not href:
                            continue

                        item_id_match = re.search(r"/marketplace/item/(\d+)", href)
                        item_id = item_id_match.group(1) if item_id_match else href
                        if item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)

                        card_text = link_elem.inner_text()
                        if not card_text:
                            continue

                        lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                        if not lines:
                            continue

                        # Extraer precio y título limpio ignorando insignias
                        price = 0
                        for line in lines:
                            price_match = re.search(r"\$\s*([0-9]{1,3}(?:\.[0-9]{3})+)", line)
                            if price_match:
                                price = int(price_match.group(1).replace(".", ""))
                                break
                            elif "$" in line:
                                clean_digits = re.sub(r"[^\d]", "", line)
                                if clean_digits and len(clean_digits) >= 6: # Precios de autos >= 100.000
                                    price = int(clean_digits)
                                    break

                        title = extract_clean_title(lines, price)

                        # FILTRO ESTRICTO: El título debe contener TODOS los tokens requeridos
                        title_lower = title.lower()
                        is_strict_match = all(token in title_lower for token in required_tokens)

                        if not is_strict_match:
                            # Intentar también con la segunda o tercera línea si el título viene fragmentado
                            full_card_lower = card_text.lower()
                            if not all(token in full_card_lower for token in required_tokens):
                                continue

                        if 500000 <= price <= 90000000:
                            extracted_prices.append(price)
                            matching_titles.append(title)
                            print(f"   [Coincidencia Estricta #{len(extracted_prices)}] {title} - ${price:,} CLP")

                    except Exception as item_err:
                        continue

                if len(seen_ids) >= max_results:
                    break

                page.evaluate("window.scrollBy(0, 900)")
                page.wait_for_timeout(1500)

            browser.close()

    except Exception as sys_err:
        print(f"[Marketplace Validation Scraper Error] {sys_err}")

    if not extracted_prices:
        return {
            "success": False,
            "sample_count": 0,
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "prices": [],
            "message": f"No se encontraron publicaciones exactas en Marketplace para '{search_query_str}'"
        }

    prices_arr = np.array(extracted_prices)
    median_val = int(round(float(np.median(prices_arr))))
    min_val = int(np.min(prices_arr))
    max_val = int(np.max(prices_arr))
    avg_val = int(round(float(np.mean(prices_arr))))

    print(f"[Marketplace Validation] Mediana calculada: ${median_val:,} CLP sobre {len(extracted_prices)} publicaciones coincidentes.")

    return {
        "success": True,
        "sample_count": len(extracted_prices),
        "median_price": median_val,
        "min_price": min_val,
        "max_price": max_val,
        "avg_price": avg_val,
        "prices": extracted_prices,
        "message": f"Mediana en Marketplace calculada exitosamente (${median_val:,} CLP) sobre {len(extracted_prices)} publicaciones coincidentes."
    }

async def get_marketplace_market_median(brand: str, model: str, year: int = None, max_results: int = 100) -> dict:
    """Wrapper asíncrono que ejecuta la función sincrónica en un hilo dedicado"""
    return await asyncio.to_thread(get_marketplace_market_median_sync, brand, model, year, max_results)

if __name__ == "__main__":
    res = asyncio.run(get_marketplace_market_median("chevrolet", "spark", 2016))
    print(res)
