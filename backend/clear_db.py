import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, SessionLocal
from models import Vehicle, SentinelConfig, FilterKeyword

def clear_vehicles():
    init_db()
    db = SessionLocal()
    try:
        count = db.query(Vehicle).count()
        db.query(Vehicle).delete()
        
        # Resetear timestamps de ejecución en la configuración
        config = db.query(SentinelConfig).first()
        if config:
            config.last_run_at = None
            config.next_run_at = None

        db.commit()
        print(f"[Clear DB] Base de datos limpiada con éxito. {count} vehículos eliminados.")
    except Exception as e:
        db.rollback()
        print(f"[Clear DB Error] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_vehicles()
