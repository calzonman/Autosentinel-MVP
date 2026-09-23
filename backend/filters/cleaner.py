import re

# Palabras de alto riesgo comercial y legal
DEFAULT_RISK_KEYWORDS = [
    r"\bprenda\b", r"\bprendado\b", r"\bprendada\b",
    r"\bembargo\b", r"\bembargado\b",
    r"\bdesarme\b", r"\bdesarmado\b", r"\bsolo repuestos\b", r"\bpara repuestos\b",
    r"\bchocado\b", r"\bchocada\b", r"\bvolcado\b", r"\bvolcada\b", r"\bsiniestro\b", r"\bsiniestrado\b",
    r"\bpanne\b", r"\bmotor malo\b", r"\bfalla de motor\b", r"\bculata\b",
    r"\bsin padron\b", r"\bsin padrón\b", r"\bsin transferencia\b", r"\bno transferible\b",
    r"\bmultas acumuladas\b", r"\bclonado\b", r"\bclonada\b"
]

# Precios engañosos / anzuelo comunes en Marketplace
DUMMY_PRICES = {1, 12, 123, 1234, 12345, 9999, 99999, 999999, 123456, 1234567, 9999999}

def validate_price(price: int, min_price: int = 300000, max_price: int = 40000000) -> tuple[bool, str]:
    if price in DUMMY_PRICES:
        return False, f"Precio engañoso detectado (${price:,})"
    if price < min_price:
        return False, f"Precio excesivamente bajo (${price:,} < ${min_price:,})"
    if price > max_price:
        return False, f"Precio excede el presupuesto máximo (${price:,} > ${max_price:,})"
    return True, ""

def validate_text(title: str, description: str = "", custom_keywords: list[str] = None) -> tuple[bool, str]:
    text_to_check = f"{title} {description}".lower()
    keywords = DEFAULT_RISK_KEYWORDS
    
    if custom_keywords:
        for kw in custom_keywords:
            pattern = r"\b" + re.escape(kw.lower()) + r"\b"
            if pattern not in keywords:
                keywords.append(pattern)

    for kw_pattern in keywords:
        match = re.search(kw_pattern, text_to_check)
        if match:
            matched_word = match.group(0)
            return False, f"Palabra de riesgo detectada: '{matched_word}'"
            
    return True, ""

def is_valid_listing(title: str, price: int, description: str = "", min_price: int = 300000, max_price: int = 40000000, custom_keywords: list[str] = None) -> tuple[bool, str]:
    price_ok, price_reason = validate_price(price, min_price, max_price)
    if not price_ok:
        return False, price_reason

    text_ok, text_reason = validate_text(title, description, custom_keywords)
    if not text_ok:
        return False, text_reason

    return True, "Válido"
