import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, SessionLocal
from models import Vehicle, SentinelConfig, FilterKeyword
from calculator.financial import calculate_financial_score

def seed():
    init_db()
    db = SessionLocal()
    
    # Asegurar configuración por defecto
    config = db.query(SentinelConfig).first()
    if not config:
        config = SentinelConfig(
            search_query="autos",
            max_budget=20000000,
            min_budget=500000,
            locations="Valparaíso, Región Metropolitana",
            interval_hours=3,
            mechanical_cushion_default=500000,
            transfer_tax_percent=1.5,
            is_active=True
        )
        db.add(config)

    # Insertar Palabras Clave de Filtrado por Defecto
    default_keywords = [
        ("prenda", "prenda"),
        ("chocado", "choque"),
        ("desarme", "fallas"),
        ("panne", "fallas"),
        ("sin padrón", "documento")
    ]
    for word, cat in default_keywords:
        if not db.query(FilterKeyword).filter(FilterKeyword.word == word).first():
            db.add(FilterKeyword(word=word, category=cat))

    # Oportunidades Demostrativas
    samples = [
        {
            "external_id": "mp_demo_101",
            "title": "Suzuki Swift 1.2 GLX 2019 Excelente Estado",
            "price": 4800000,
            "estimated_market_price": 7200000,
            "brand": "Suzuki",
            "model": "Swift",
            "year": 2019,
            "location": "Viña del Mar, Valparaíso",
            "url": "https://www.facebook.com/marketplace/item/101demo",
            "image_url": "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=600&auto=format&fit=crop&q=80"
        },
        {
            "external_id": "mp_demo_102",
            "title": "Hyundai Accent 1.4 RB 2017 Único Dueño",
            "price": 5200000,
            "estimated_market_price": 6900000,
            "brand": "Hyundai",
            "model": "Accent",
            "year": 2017,
            "location": "Santiago, Región Metropolitana",
            "url": "https://www.facebook.com/marketplace/item/102demo",
            "image_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600&auto=format&fit=crop&q=80"
        },
        {
            "external_id": "mp_demo_103",
            "title": "Nissan Versa 1.6 Sense 2020 Impecable",
            "price": 7900000,
            "estimated_market_price": 8500000,
            "brand": "Nissan",
            "model": "Versa",
            "year": 2020,
            "location": "Quilpué, Valparaíso",
            "url": "https://www.facebook.com/marketplace/item/103demo",
            "image_url": "https://images.unsplash.com/photo-1590362891991-f776e747a588?w=600&auto=format&fit=crop&q=80"
        }
    ]

    for item in samples:
        existing = db.query(Vehicle).filter(Vehicle.external_id == item["external_id"]).first()
        if not existing:
            fin = calculate_financial_score(
                published_price=item["price"],
                estimated_market_price=item["estimated_market_price"],
                mechanical_cushion=500000,
                transfer_tax_percent=1.5
            )
            vehicle = Vehicle(
                external_id=item["external_id"],
                title=item["title"],
                price=item["price"],
                estimated_market_price=item["estimated_market_price"],
                brand=item["brand"],
                model=item["model"],
                year=item["year"],
                location=item["location"],
                url=item["url"],
                image_url=item["image_url"],
                score=fin["score"],
                transfer_tax=fin["transfer_tax"],
                mechanical_cushion=500000,
                calculated_margin=fin["margin"]
            )
            db.add(vehicle)

    db.commit()
    db.close()
    print("[Seed] Oportunidades demostrativas e inicialización creadas con éxito.")

if __name__ == "__main__":
    seed()
