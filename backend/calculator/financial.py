def calculate_financial_score(
    published_price: int,
    estimated_market_price: int,
    mechanical_cushion: int = 500000,
    transfer_tax_percent: float = 1.5
) -> dict:
    """
    Calcula el costo total de adquisición, impuesto de transferencia, margen neto ($ CLP)
    y evalúa el Score de Semáforo dinámicamente según el PORCENTAJE de margen sobre la inversión total:
    
    - VERDE: Porcentaje de Margen >= 30%
    - AMARILLO: 15% <= Porcentaje de Margen < 30%
    - ROJO: Porcentaje de Margen < 15%
    """
    if published_price <= 0:
        return {
            "transfer_tax": 0,
            "total_cost": 0,
            "margin": 0,
            "margin_percent": 0.0,
            "score": "ROJO",
            "reason": "Precio publicado inválido"
        }

    # Impuesto de transferencia (costos duros)
    transfer_tax = int(round(published_price * (transfer_tax_percent / 100.0)))
    
    # Costo total = Vehículo + Impuesto de Transferencia + Colchón Mecánico
    total_cost = published_price + transfer_tax + mechanical_cushion
    
    # Si no se ha realizado validación de mercado aún
    if estimated_market_price <= 0:
        return {
            "transfer_tax": transfer_tax,
            "total_cost": total_cost,
            "margin": 0,
            "margin_percent": 0.0,
            "score": "AMARILLO",
            "reason": "Pendiente de validación de mercado en Chileautos"
        }

    margin = estimated_market_price - total_cost
    margin_percent = (margin / total_cost) * 100.0

    if margin_percent >= 30.0:
        score = "VERDE"
    elif margin_percent >= 15.0:
        score = "AMARILLO"
    else:
        score = "ROJO"

    return {
        "transfer_tax": transfer_tax,
        "total_cost": total_cost,
        "margin": int(round(margin)),
        "margin_percent": round(margin_percent, 2),
        "score": score,
        "reason": f"Margen: {round(margin_percent, 2)}% (${int(round(margin)):,} CLP)"
    }
