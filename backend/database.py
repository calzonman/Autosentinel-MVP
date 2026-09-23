import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automotive_mvp.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

    # Migración automática de columnas para SQLite existente
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(vehicles)")
            existing_cols = {row[1] for row in cursor.fetchall()}

            new_cols = [
                ("score_chileautos", "TEXT DEFAULT 'PENDIENTE'"),
                ("estimated_market_price_chileautos", "INTEGER DEFAULT 0"),
                ("transfer_tax_chileautos", "INTEGER DEFAULT 0"),
                ("margin_chileautos", "INTEGER DEFAULT 0"),
                ("samples_count_chileautos", "INTEGER DEFAULT 0"),
                ("min_price_chileautos", "INTEGER DEFAULT 0"),
                ("max_price_chileautos", "INTEGER DEFAULT 0"),
                ("avg_price_chileautos", "INTEGER DEFAULT 0"),
                ("score_mp", "TEXT DEFAULT 'PENDIENTE'"),
                ("estimated_market_price_mp", "INTEGER DEFAULT 0"),
                ("transfer_tax_mp", "INTEGER DEFAULT 0"),
                ("margin_mp", "INTEGER DEFAULT 0"),
                ("samples_count_mp", "INTEGER DEFAULT 0"),
                ("min_price_mp", "INTEGER DEFAULT 0"),
                ("max_price_mp", "INTEGER DEFAULT 0"),
                ("avg_price_mp", "INTEGER DEFAULT 0"),
            ]

            for col_name, col_type in new_cols:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {col_name} {col_type}")
                    print(f"[DB Migration] Agregada columna '{col_name}' a la tabla 'vehicles'.")

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB Migration Warning] {e}")

if __name__ == "__main__":
    init_db()
