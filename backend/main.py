import os
import json
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import init_db, get_db
from models import Vehicle, SentinelConfig, FilterKeyword
from calculator.financial import calculate_financial_score
from scrapers.chileautos_micro import get_chileautos_market_median
from scrapers.marketplace_micro import get_marketplace_market_median
from scrapers.marketplace_sentinel import run_marketplace_sentinel
from scrapers.auth_helper import login_and_save_session, is_session_saved, AUTH_FILE
from export.google_sheets import export_vehicles_to_google_sheets, CREDENTIALS_FILE

from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI(
    title="Sistema de Análisis y Detección de Oportunidades Automotrices",
    version="1.0.0"
)

# Permitir solicitudes CORS desde el frontend en Svelte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

# Esquemas Pydantic
class ConfigSchema(BaseModel):
    search_query: str = "autos"
    max_budget: int = 20000000
    min_budget: int = 500000
    locations: str = "Valparaíso, Región Metropolitana"
    interval_hours: int = 3
    mechanical_cushion_default: int = 500000
    transfer_tax_percent: float = 1.5
    is_active: bool = True

class ExportSchema(BaseModel):
    spreadsheet_id: str
    vehicle_ids: list[int] = []

class RecalculateSchema(BaseModel):
    mechanical_cushion: int
    estimated_market_price: int = None

class MarketValidateSchema(BaseModel):
    brand: str
    model: str
    year: int = None

@app.on_event("startup")
async def startup_event():
    init_db()
    print("[FastAPI] Base de datos SQLite inicializada.")
    
    # Iniciar programador de tareas en segundo plano
    scheduler.add_job(
        scheduled_sentinel_job,
        'interval',
        hours=3,
        id='sentinel_job',
        replace_existing=True
    )
    scheduler.start()
    print("[APScheduler] Centinela programado cada 3 horas.")

async def scheduled_sentinel_job():
    print(f"[{datetime.now().isoformat()}] Ejecutando tarea programada del Centinela...")
    res = await run_marketplace_sentinel()
    print(f"[Centinela Programado Resultado] {res}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Vehicle).count()
    verde = db.query(Vehicle).filter(Vehicle.score == "VERDE").count()
    amarillo = db.query(Vehicle).filter(Vehicle.score == "AMARILLO").count()
    rojo = db.query(Vehicle).filter(Vehicle.score == "ROJO").count()
    invalido = db.query(Vehicle).filter(Vehicle.score == "INVALIDO").count()
    
    config = db.query(SentinelConfig).first()
    last_run = config.last_run_at.isoformat() if config and config.last_run_at else None
    
    return {
        "total_vehicles": total,
        "score_verde": verde,
        "score_amarillo": amarillo,
        "score_rojo": rojo,
        "discarded_invalido": invalido,
        "last_run_at": last_run,
        "session_saved": is_session_saved()
    }

@app.get("/api/vehicles")
def list_vehicles(
    score: str = None,
    only_valid: bool = True,
    search: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Vehicle)
    
    if only_valid:
        query = query.filter(Vehicle.score != "INVALIDO")
    if score:
        query = query.filter(Vehicle.score == score.upper())
    if search:
        query = query.filter(Vehicle.title.ilike(f"%{search}%"))
        
    query = query.order_by(Vehicle.created_at.desc())
    total = query.count()
    vehicles = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "vehicles": vehicles
    }

@app.get("/api/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehicle

@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """
    Elimina un vehículo específico de la base de datos por su ID único.
    
    @param vehicle_id: ID numérico del vehículo a eliminar.
    @return: Mensaje de confirmación de eliminación.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    db.delete(vehicle)
    db.commit()
    return {"message": f"Vehículo con ID {vehicle_id} eliminado exitosamente."}

@app.delete("/api/vehicles")
def delete_all_vehicles(db: Session = Depends(get_db)):
    """
    Limpia y purga la totalidad de los registros de vehículos recopilados por los scrappers.
    
    @return: Resumen con la cantidad de filas eliminadas.
    """
    deleted_count = db.query(Vehicle).delete()
    db.commit()
    return {"message": "Toda la información de vehículos ha sido eliminada exitosamente.", "deleted_count": deleted_count}

@app.post("/api/vehicles/{vehicle_id}/validate-market")
async def validate_market_price(vehicle_id: int, body: MarketValidateSchema, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    try:
        config = db.query(SentinelConfig).first()
        transfer_tax_pct = config.transfer_tax_percent if config else 1.5

        # 1. Ejecutar micro-scrapers de Chileautos y Facebook Marketplace
        chileautos_res = await get_chileautos_market_median(body.brand, body.model, body.year)
        mp_res = await get_marketplace_market_median(body.brand, body.model, body.year, max_results=100)

        vehicle.brand = body.brand
        vehicle.model = body.model
        if body.year:
            vehicle.year = body.year

        # 2. Calcular métricas para Chileautos
        if chileautos_res.get("success") and chileautos_res.get("median_price", 0) > 0:
            median_ca = chileautos_res["median_price"]
            fin_ca = calculate_financial_score(
                published_price=vehicle.price,
                estimated_market_price=median_ca,
                mechanical_cushion=vehicle.mechanical_cushion,
                transfer_tax_percent=transfer_tax_pct
            )
            vehicle.estimated_market_price_chileautos = median_ca
            vehicle.transfer_tax_chileautos = fin_ca["transfer_tax"]
            vehicle.margin_chileautos = fin_ca["margin"]
            vehicle.score_chileautos = fin_ca["score"]
            vehicle.samples_count_chileautos = chileautos_res.get("sample_count", 0)
            vehicle.min_price_chileautos = chileautos_res.get("min_price", 0)
            vehicle.max_price_chileautos = chileautos_res.get("max_price", 0)
            vehicle.avg_price_chileautos = chileautos_res.get("avg_price", median_ca)

        # 3. Calcular métricas para Facebook Marketplace
        if mp_res.get("success") and mp_res.get("median_price", 0) > 0:
            median_mp = mp_res["median_price"]
            fin_mp = calculate_financial_score(
                published_price=vehicle.price,
                estimated_market_price=median_mp,
                mechanical_cushion=vehicle.mechanical_cushion,
                transfer_tax_percent=transfer_tax_pct
            )
            vehicle.estimated_market_price_mp = median_mp
            vehicle.transfer_tax_mp = fin_mp["transfer_tax"]
            vehicle.margin_mp = fin_mp["margin"]
            vehicle.score_mp = fin_mp["score"]
            vehicle.samples_count_mp = mp_res.get("sample_count", 0)
            vehicle.min_price_mp = mp_res.get("min_price", 0)
            vehicle.max_price_mp = mp_res.get("max_price", 0)
            vehicle.avg_price_mp = mp_res.get("avg_price", median_mp)

        # 4. Actualizar campos globales por compatibilidad
        if vehicle.estimated_market_price_chileautos > 0:
            vehicle.estimated_market_price = vehicle.estimated_market_price_chileautos
            vehicle.transfer_tax = vehicle.transfer_tax_chileautos
            vehicle.calculated_margin = vehicle.margin_chileautos
            vehicle.score = vehicle.score_chileautos
        elif vehicle.estimated_market_price_mp > 0:
            vehicle.estimated_market_price = vehicle.estimated_market_price_mp
            vehicle.transfer_tax = vehicle.transfer_tax_mp
            vehicle.calculated_margin = vehicle.margin_mp
            vehicle.score = vehicle.score_mp

        db.commit()
        db.refresh(vehicle)

        return {
            "vehicle": vehicle,
            "chileautos_stats": chileautos_res,
            "marketplace_stats": mp_res,
            "market_stats": chileautos_res
        }
    except Exception as e:
        print(f"[Validate Market Error] {e}")
        return {
            "vehicle": vehicle,
            "chileautos_stats": {"success": False, "median_price": 0, "sample_count": 0, "message": str(e)},
            "marketplace_stats": {"success": False, "median_price": 0, "sample_count": 0, "message": str(e)},
            "market_stats": {"success": False, "median_price": 0, "sample_count": 0, "message": str(e)}
        }

@app.post("/api/vehicles/{vehicle_id}/recalculate")
def recalculate_vehicle_score(vehicle_id: int, body: RecalculateSchema, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    config = db.query(SentinelConfig).first()
    transfer_tax_pct = config.transfer_tax_percent if config else 1.5

    vehicle.mechanical_cushion = body.mechanical_cushion

    # Recalcular Chileautos si existe precio estimado
    if vehicle.estimated_market_price_chileautos > 0:
        fin_ca = calculate_financial_score(
            published_price=vehicle.price,
            estimated_market_price=vehicle.estimated_market_price_chileautos,
            mechanical_cushion=vehicle.mechanical_cushion,
            transfer_tax_percent=transfer_tax_pct
        )
        vehicle.transfer_tax_chileautos = fin_ca["transfer_tax"]
        vehicle.margin_chileautos = fin_ca["margin"]
        vehicle.score_chileautos = fin_ca["score"]

    # Recalcular Marketplace si existe precio estimado
    if vehicle.estimated_market_price_mp > 0:
        fin_mp = calculate_financial_score(
            published_price=vehicle.price,
            estimated_market_price=vehicle.estimated_market_price_mp,
            mechanical_cushion=vehicle.mechanical_cushion,
            transfer_tax_percent=transfer_tax_pct
        )
        vehicle.transfer_tax_mp = fin_mp["transfer_tax"]
        vehicle.margin_mp = fin_mp["margin"]
        vehicle.score_mp = fin_mp["score"]

    if vehicle.estimated_market_price_chileautos > 0:
        vehicle.estimated_market_price = vehicle.estimated_market_price_chileautos
        vehicle.transfer_tax = vehicle.transfer_tax_chileautos
        vehicle.calculated_margin = vehicle.margin_chileautos
        vehicle.score = vehicle.score_chileautos
    elif vehicle.estimated_market_price_mp > 0:
        vehicle.estimated_market_price = vehicle.estimated_market_price_mp
        vehicle.transfer_tax = vehicle.transfer_tax_mp
        vehicle.calculated_margin = vehicle.margin_mp
        vehicle.score = vehicle.score_mp

    db.commit()
    db.refresh(vehicle)
    return vehicle

@app.post("/api/sentinel/run")
async def trigger_sentinel(background_tasks: BackgroundTasks, max_items: int = 10):
    background_tasks.add_task(run_marketplace_sentinel, max_items)
    return {"message": f"Centinela iniciado en segundo plano (límite {max_items} publicaciones)."}

@app.get("/api/config")
def get_config(db: Session = Depends(get_db)):
    config = db.query(SentinelConfig).first()
    if not config:
        config = SentinelConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
        
    keywords = db.query(FilterKeyword).all()
    return {
        "config": config,
        "filter_keywords": keywords
    }

@app.put("/api/config")
def update_config(body: ConfigSchema, db: Session = Depends(get_db)):
    """
    Actualiza la configuración global del sistema y aplica los parámetros dinámicamente:
    
    1. Mantiene fijos los valores de búsqueda ('autos') y regiones ('Valparaíso, Región Metropolitana').
    2. Reprograma el intervalo del robot Centinela en APScheduler según 'interval_hours'.
    3. Ejecuta un recálculo masivo sobre los vehículos almacenados para actualizar los impuestos 
       de transferencia, márgenes netos y scores del Semáforo con los nuevos parámetros.
    """
    config = db.query(SentinelConfig).first()
    if not config:
        config = SentinelConfig()
        db.add(config)
        
    # Mantener fijos los valores obligatorios del modelo de negocio
    config.search_query = "autos"
    config.locations = "Valparaíso, Región Metropolitana"
    
    # Aplicar nuevos parámetros configurables
    config.max_budget = body.max_budget
    config.min_budget = body.min_budget
    config.interval_hours = body.interval_hours
    config.mechanical_cushion_default = body.mechanical_cushion_default
    config.transfer_tax_percent = body.transfer_tax_percent
    config.is_active = body.is_active

    db.commit()

    # Reprogramar dinámicamente la frecuencia de ejecución del Centinela en APScheduler
    try:
        scheduler.reschedule_job('sentinel_job', trigger='interval', hours=body.interval_hours)
        print(f"[APScheduler] Tarea reprogramada exitosamente a un intervalo de {body.interval_hours} horas.")
    except Exception as sched_err:
        print(f"[APScheduler Reprogramación Warning] {sched_err}")

    # Recálculo masivo de la base de datos para aplicar la nueva tasa de impuesto y colchón
    try:
        vehicles = db.query(Vehicle).all()
        for vehicle in vehicles:
            # Recalcular Chileautos si posee mediana estimada
            if vehicle.estimated_market_price_chileautos > 0:
                fin_ca = calculate_financial_score(
                    published_price=vehicle.price,
                    estimated_market_price=vehicle.estimated_market_price_chileautos,
                    mechanical_cushion=vehicle.mechanical_cushion,
                    transfer_tax_percent=body.transfer_tax_percent
                )
                vehicle.transfer_tax_chileautos = fin_ca["transfer_tax"]
                vehicle.margin_chileautos = fin_ca["margin"]
                vehicle.score_chileautos = fin_ca["score"]

            # Recalcular Marketplace si posee mediana estimada
            if vehicle.estimated_market_price_mp > 0:
                fin_mp = calculate_financial_score(
                    published_price=vehicle.price,
                    estimated_market_price=vehicle.estimated_market_price_mp,
                    mechanical_cushion=vehicle.mechanical_cushion,
                    transfer_tax_percent=body.transfer_tax_percent
                )
                vehicle.transfer_tax_mp = fin_mp["transfer_tax"]
                vehicle.margin_mp = fin_mp["margin"]
                vehicle.score_mp = fin_mp["score"]

            # Sincronizar campos principales de compatibilidad
            if vehicle.estimated_market_price_chileautos > 0:
                vehicle.transfer_tax = vehicle.transfer_tax_chileautos
                vehicle.calculated_margin = vehicle.margin_chileautos
                vehicle.score = vehicle.score_chileautos
            elif vehicle.estimated_market_price_mp > 0:
                vehicle.transfer_tax = vehicle.transfer_tax_mp
                vehicle.calculated_margin = vehicle.margin_mp
                vehicle.score = vehicle.score_mp

        db.commit()
        db.refresh(config)
        print(f"[Config Auto-Recálculo] Se actualizaron {len(vehicles)} vehículos con la nueva tasa de impuesto ({body.transfer_tax_percent}%).")
    except Exception as recalc_err:
        db.rollback()
        print(f"[Config Recálculo Error] {recalc_err}")

    return config

@app.post("/api/auth/facebook")
def trigger_facebook_auth():
    import subprocess
    import sys
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers", "auth_helper.py")
    subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(os.path.abspath(__file__)))
    return {"message": "Ventana de navegador (headed) abierta para iniciar sesión en Facebook. Las cookies se guardarán en auth.json automáticamente."}

@app.get("/api/auth/facebook/status")
def get_facebook_auth_status():
    return {
        "session_saved": is_session_saved(),
        "auth_file_exists": os.path.exists(os.path.abspath(AUTH_FILE))
    }

@app.post("/api/auth/google-sheets/credentials")
async def upload_google_credentials(file: UploadFile = File(...)):
    creds_path = os.path.abspath(CREDENTIALS_FILE)
    content = await file.read()
    with open(creds_path, "wb") as f:
        f.write(content)
    return {"message": "Archivo service_account.json guardado correctamente."}

@app.post("/api/export-sheets")
def export_to_sheets(body: ExportSchema):
    res = export_vehicles_to_google_sheets(
        spreadsheet_id=body.spreadsheet_id,
        vehicle_ids=body.vehicle_ids
    )
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
