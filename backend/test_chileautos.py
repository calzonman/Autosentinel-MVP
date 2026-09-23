import urllib.parse
import re
import numpy as np
from playwright.sync_api import sync_playwright

def inspect_chileautos(brand: str, model: str, year: int = None):
    query_str = f"CarAll.keyword({brand} {model} {year})." if year else f"CarAll.keyword({brand} {model})."
    encoded_q = urllib.parse.quote(query_str)
    url = f"https://www.chileautos.cl/vehiculos/?q={encoded_q}"
    print(f"[Inspect Chileautos] URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=35000)
            print(f"[Inspect Chileautos] Title: {page.title()}")
            page.wait_for_timeout(4000)

            # Hacer scroll
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(2000)

            html = page.content()
            body_text = page.inner_text("body")

            print(f"[Inspect Chileautos] HTML Length: {len(html)}")
            print(f"[Inspect Chileautos] Body Text Length: {len(body_text)}")

            # Buscar precios con formato $ X.XXX.XXX o $XX.XXX.XXX o números sueltos
            formatted_prices = re.findall(r"\$\s*([0-9]{1,3}(?:\.[0-9]{3})+)", html + " " + body_text)
            clp_digits = re.findall(r'\b[3-9]\d{6,7}\b', html)

            all_extracted = []
            for fp in formatted_prices:
                val = int(fp.replace(".", ""))
                if 500000 <= val <= 90000000:
                    all_extracted.append(val)

            for cd in clp_digits:
                val = int(cd)
                if 500000 <= val <= 90000000:
                    all_extracted.append(val)

            print(f"[Inspect Chileautos] Total Precios Extraídos: {len(all_extracted)}")
            if all_extracted:
                arr = np.array(all_extracted)
                q10, q90 = np.percentile(arr, 10), np.percentile(arr, 90)
                filtered = arr[(arr >= q10) & (arr <= q90)]
                if len(filtered) == 0:
                    filtered = arr
                median_val = int(round(float(np.median(filtered))))
                print(f"[Inspect Chileautos] MEDIANA CALCULADA: ${median_val:,}")
                return {
                    "success": True,
                    "median_price": median_val,
                    "sample_count": len(all_extracted),
                    "min_price": int(np.min(filtered)),
                    "max_price": int(np.max(filtered))
                }
            else:
                print("[Inspect Chileautos] ⚠️ No se detectaron precios.")
                return {"success": False, "sample_count": 0}

        except Exception as e:
            print(f"[Inspect Chileautos Error] {e}")
            return {"success": False, "error": str(e)}
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_chileautos("chevrolet", "spark", 2019)
