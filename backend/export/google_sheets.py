import os
import gspread
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Vehicle

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "service_account.json")

def export_vehicles_to_google_sheets(spreadsheet_id: str, vehicle_ids: list[int] = None) -> dict:
    """
    Inyecta los vehículos seleccionados o aprobados en la hoja de Google Sheets especificada
    usando la Service Account configurada.
    """
    creds_path = os.path.abspath(CREDENTIALS_FILE)
    if not os.path.exists(creds_path):
        return {
            "success": False,
            "message": f"Archivo de credenciales 'service_account.json' no encontrado en {creds_path}"
        }

    db: Session = SessionLocal()
    try:
        if vehicle_ids:
            vehicles = db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()
        else:
            vehicles = db.query(Vehicle).filter(
                Vehicle.score != "INVALIDO",
                Vehicle.exported_to_sheets == False
            ).all()

        if not vehicles:
            return {
                "success": True,
                "exported_count": 0,
                "message": "No hay vehículos pendientes por exportar a Google Sheets."
            }

        client = gspread.service_account(filename=creds_path)
        sheet = client.open_by_key(spreadsheet_id).sheet1

        expected_headers = [
            "ID", "Título", "Precio Publicado", "Mediana Chileautos",
            "Impuesto Transf.", "Colchón Mecánico", "Margen ($)",
            "Score", "Ubicación", "URL Marketplace", "Fecha Detección"
        ]

        existing_values = sheet.get_all_values()
        if not existing_values:
            sheet.append_row(expected_headers)

        rows_to_append = []
        for v in vehicles:
            rows_to_append.append([
                v.id,
                v.title,
                f"${v.price:,}",
                f"${v.estimated_market_price:,}" if v.estimated_market_price else "N/A",
                f"${v.transfer_tax:,}",
                f"${v.mechanical_cushion:,}",
                f"${v.calculated_margin:,}" if v.calculated_margin else "N/A",
                v.score,
                v.location or "Desconocida",
                v.url,
                v.created_at.strftime("%Y-%m-%d %H:%M") if v.created_at else datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            v.exported_to_sheets = True

        sheet.append_rows(rows_to_append)
        db.commit()

        return {
            "success": True,
            "exported_count": len(rows_to_append),
            "message": f"Se exportaron exitosamente {len(rows_to_append)} vehículos a Google Sheets."
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error al exportar a Google Sheets: {str(e)}"}
    finally:
        db.close()
