import os
import re
import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright

from database import SessionLocal
from models import Vehicle, SentinelConfig, FilterKeyword
from filters.cleaner import is_valid_listing
from calculator.financial import calculate_financial_score
from scrapers.auth_helper import AUTH_FILE

TARGET_MARKETPLACE_URL = "https://www.facebook.com/marketplace/106039289436408/search?daysSinceListed=1&sortBy=best_match&query=Veh%C3%ADculos&category_id=546583916084032&exact=false&referral_ui_component=category_menu_item"

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

        # Omitir insignias de estado comunes
        if clean_lower in BADGE_TAGS:
            continue
        # Omitir líneas que sean únicamente un precio o comiencen por $
        if clean.startswith("$") or (price > 0 and clean.replace(".", "").replace("$", "").strip().isdigit()):
            continue
        # Omitir metadatos de tiempo ("hace 2 horas", "hace 1 día")
        if clean_lower.startswith("hace ") and any(unit in clean_lower for unit in ["hora", "día", "dia", "minuto"]):
            continue

        return clean

    return lines[0] if lines else "Vehículo sin título"

def run_marketplace_sentinel_sync(max_items: int = 20) -> dict:
    """
    Motor Centinela sincrónico: Scrapea las primeras `max_items` publicaciones del enlace especificado
    de Facebook Marketplace usando sync_playwright en un hilo secundario dedicado.
    """
    db: Session = SessionLocal()
    try:
        config = db.query(SentinelConfig).first()
        if not config:
            config = SentinelConfig()
            db.add(config)
            db.commit()
            db.refresh(config)

        # Cargar palabras clave custom activas de la BD
        custom_kw_objs = db.query(FilterKeyword).filter(FilterKeyword.is_active == True).all()
        custom_keywords = [k.word for k in custom_kw_objs]

        # Comprobar si existe archivo de sesión auth.json
        auth_path = os.path.abspath(AUTH_FILE)
        use_auth = os.path.exists(auth_path) and os.path.getsize(auth_path) > 50

        processed_count = 0
        new_valid_count = 0
        discarded_count = 0
        seen_ids = set()

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
                print(f"[Centinela] Reutilizando sesión autenticada desde {auth_path}")
            else:
                print("[Centinela] Ejecutando sin auth.json (modo visitante)")

            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            print(f"[Centinela] Navegando a la URL objetivo en Marketplace ({max_items} ítems máx)...")
            page.goto(TARGET_MARKETPLACE_URL, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            # Scroll progresivo para cargar elementos
            for scroll_step in range(6):
                if processed_count >= max_items:
                    break

                links = page.query_selector_all("a[href*='/marketplace/item/']")
                print(f"[Centinela Scroll {scroll_step+1}] Enlaces detectados en DOM: {len(links)}")

                for link_elem in links:
                    if processed_count >= max_items:
                        break

                    try:
                        href = link_elem.get_attribute("href")
                        if not href:
                            continue

                        full_url = f"https://www.facebook.com{href}" if href.startswith("/") else href
                        item_id_match = re.search(r"/marketplace/item/(\d+)", full_url)
                        external_id = item_id_match.group(1) if item_id_match else full_url

                        if external_id in seen_ids:
                            continue
                        seen_ids.add(external_id)

                        card_text = link_elem.inner_text()
                        if not card_text:
                            continue

                        lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                        if not lines:
                            continue

                        price = 0
                        for line in lines:
                            price_match = re.search(r"\$\s*([0-9]{1,3}(?:\.[0-9]{3})+)", line)
                            if price_match:
                                price = int(price_match.group(1).replace(".", ""))
                                break
                            elif "$" in line:
                                clean_digits = re.sub(r"[^\d]", "", line)
                                if clean_digits and len(clean_digits) >= 5:
                                    price = int(clean_digits)
                                    break

                        # Extraer título real descartando insignias como "Recién publicado", "Nuevo", etc.
                        title = extract_clean_title(lines, price)

                        location = "Valparaíso / RM"
                        for line in lines:
                            if any(loc in line.lower() for loc in ["valparaíso", "viña", "santiago", "quillota", "quilpué", "rancagua", "maipú", "la florida", "providencia", "san bernardo", "puente alto"]):
                                location = line
                                break

                        img_elem = link_elem.query_selector("img")
                        image_url = img_elem.get_attribute("src") if img_elem else None

                        processed_count += 1
                        print(f"[Centinela Extraído #{processed_count}] {title} - ${price:,} ({location})")

                        existing = db.query(Vehicle).filter(Vehicle.external_id == external_id).first()
                        
                        is_valid, reason = is_valid_listing(
                            title=title,
                            price=price,
                            description="",
                            min_price=config.min_budget,
                            max_price=config.max_budget,
                            custom_keywords=custom_keywords
                        )

                        if not is_valid:
                            discarded_count += 1
                            if not existing:
                                db.add(Vehicle(
                                    external_id=external_id,
                                    title=title,
                                    price=price,
                                    location=location,
                                    url=full_url,
                                    image_url=image_url,
                                    score="INVALIDO",
                                    discarded_reason=reason,
                                    raw_description=card_text
                                ))
                                db.commit()
                            continue

                        fin_res = calculate_financial_score(
                            published_price=price,
                            estimated_market_price=0,
                            mechanical_cushion=config.mechanical_cushion_default,
                            transfer_tax_percent=config.transfer_tax_percent
                        )

                        new_valid_count += 1
                        if existing:
                            existing.title = title
                            existing.price = price
                            existing.location = location
                            existing.image_url = image_url or existing.image_url
                        else:
                            db.add(Vehicle(
                                external_id=external_id,
                                title=title,
                                price=price,
                                location=location,
                                url=full_url,
                                image_url=image_url,
                                score=fin_res["score"],
                                transfer_tax=fin_res["transfer_tax"],
                                mechanical_cushion=config.mechanical_cushion_default,
                                raw_description=card_text
                            ))
                        db.commit()

                    except Exception as item_err:
                        print(f"[Centinela Item Error] {item_err}")
                        continue

                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1500)

            browser.close()

        config.last_run_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "success": True,
            "processed_count": processed_count,
            "new_valid_count": new_valid_count,
            "discarded_count": discarded_count,
            "target_url": TARGET_MARKETPLACE_URL,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        db.rollback()
        print(f"[Centinela Error Global] {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

async def run_marketplace_sentinel(max_items: int = 20) -> dict:
    """Wrapper asíncrono que ejecuta la función sincrónica del Centinela en un hilo dedicado"""
    return await asyncio.to_thread(run_marketplace_sentinel_sync, max_items)

if __name__ == "__main__":
    res = run_marketplace_sentinel_sync(max_items=20)
    print(res)
