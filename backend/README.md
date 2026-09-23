# ⚙️ AutoSentinel Backend - Servidor REST API, Motor de Scraping & Evaluación Financiera

Módulo de servidor backend desarrollado en **Python 3.13** con **FastAPI**, **Playwright**, **SQLAlchemy** y **APScheduler**. Encargado de la extracción automatizada de datos en Facebook Marketplace y Chileautos, evaluación de costos ocultos y rentabilidad, filtrado de riesgo comercial y exportación remota a Google Sheets.

---

## 📂 Estructura de Directorios (`backend/`)

```text
backend/
├── calculator/
│   └── financial.py            # Motor de cálculo financiero y semáforo de rentabilidad
├── export/
│   └── google_sheets.py        # Módulo de integración remota con Google Sheets API
├── filters/
│   └── cleaner.py              # Motor de filtrado de descarte y riesgo comercial/legal
├── scrapers/
│   ├── auth_helper.py          # Helper de captura y guardado de sesión de Facebook (Playwright)
│   ├── chileautos_micro.py     # Micro-scraper de validación de mercado en Chileautos
│   ├── marketplace_micro.py   # Micro-scraper de validación con filtro estricto en Marketplace
│   └── marketplace_sentinel.py # Motor Centinela para escaneo automatizado en Marketplace
├── auth.json.example           # Plantilla de ejemplo para auth.json (sesión Facebook)
├── service_account.json.example # Plantilla de ejemplo para service_account.json (Google Sheets)
├── database.py                 # Conexión SQLAlchemy con auto-migración SQLite
├── main.py                     # Servidor FastAPI principal, scheduler y endpoints de la API
├── models.py                   # Modelos ORM (Vehicle, SentinelConfig, FilterKeyword)
├── requirements.txt            # Especificación de dependencias de Python
├── seed_data.py                # Poblamiento inicial de vehículos demostrativos
├── clear_db.py                 # Script utilitario de purga completa de la BD
├── test_chileautos.py          # Script de prueba e inspección rápida de Chileautos
└── test_exact_chileautos.py    # Script de prueba con coincidencia exacta para Chileautos
```

---

## 🛠️ Tecnologías y Librerías

- **FastAPI (`>=0.110.0`):** Framework REST asíncrono de alto rendimiento.
- **Uvicorn (`>=0.28.0`):** Servidor ASGI para ejecución de FastAPI.
- **Playwright (`>=1.42.0`):** Automatización de navegadores headless y headed (Chromium).
- **SQLAlchemy (`>=2.0.0`):** ORM relacional para gestión de datos.
- **SQLite:** Base de datos relacional integrada en archivo local (`automotive_mvp.db`).
- **APScheduler (`>=3.10.0`):** Programador asíncrono de tareas en segundo plano.
- **gspread (`>=6.0.0`):** Cliente de integración con Google Sheets API v4.
- **Pydantic (`>=2.6.0`):** Validación estricta de esquemas de datos de entrada/salida.

---

## 💻 Instalación y Ejecución Local

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.13 o superior.

### 2. Creación del Entorno Virtual
```bash
cd backend
python -m venv venv

# Activar en Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Activar en Linux/macOS:
source venv/bin/activate
```

### 3. Instalación de Dependencias
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Inicializar Datos de Demostración (Opcional)
```bash
python seed_data.py
```

### 5. Iniciar el Servidor API
```bash
python main.py
# O usando uvicorn directamente:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
La documentación interactiva Swagger UI estará disponible en: **`http://127.0.0.1:8000/docs`**.

---

## 📡 Referencia de la API REST

### 🏥 Estado del Sistema
| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Retorna el estado operativo de la API y timestamp UTC. |
| `GET` | `/api/stats` | Retorna métricas globales (conteo por semáforo, última ejecución y estado de autenticación en Facebook). |

---

### 🚗 Gestión de Vehículos (`/api/vehicles`)

#### 1. Listar Vehículos
- **Método:** `GET /api/vehicles`
- **Query Params:**
  - `score` (opcional): `"VERDE"`, `"AMARILLO"`, `"ROJO"`, `"INVALIDO"`.
  - `only_valid` (default: `true`): Excluye vehículos descartados por el filtro.
  - `search` (opcional): Filtro de texto por título de vehículo.
  - `limit` (default: `100`), `offset` (default: `0`).

#### 2. Obtener Vehículo por ID
- **Método:** `GET /api/vehicles/{vehicle_id}`

#### 3. Eliminar Vehículo
- **Método:** `DELETE /api/vehicles/{vehicle_id}`

#### 4. Borrado Masivo / Purga de Datos
- **Método:** `DELETE /api/vehicles`
- **Descripción:** Elimina todos los registros recopilados para reiniciar las búsquedas.

#### 5. Validar Mercado Dual (Chileautos vs Marketplace)
- **Método:** `POST /api/vehicles/{vehicle_id}/validate-market`
- **Body JSON:**
  ```json
  {
    "brand": "Suzuki",
    "model": "Swift",
    "year": 2019
  }
  ```
- **Descripción:** Ejecuta en paralelo los micro-scrapers de Chileautos y Facebook Marketplace, calcula las medianas de precio, mínimos, máximos y actualiza el marcador financiero del vehículo.

#### 6. Recalcular Financiero
- **Método:** `POST /api/vehicles/{vehicle_id}/recalculate`
- **Body JSON:**
  ```json
  {
    "mechanical_cushion": 600000
  }
  ```

---

### 🤖 Robot Centinela y Configuración

#### 1. Disparar Centinela Manualmente
- **Método:** `POST /api/sentinel/run?max_items=10`
- **Descripción:** Inicia el escaneo asíncrono en segundo plano para procesar hasta `max_items` publicaciones en Facebook Marketplace.

#### 2. Consultar Configuración Global
- **Método:** `GET /api/config`

#### 3. Actualizar Configuración y Recálculo Masivo
- **Método:** `PUT /api/config`
- **Body JSON:**
  ```json
  {
    "search_query": "autos",
    "min_budget": 500000,
    "max_budget": 20000000,
    "locations": "Valparaíso, Región Metropolitana",
    "interval_hours": 3,
    "mechanical_cushion_default": 500000,
    "transfer_tax_percent": 1.5,
    "is_active": true
  }
  ```
- **Efecto secundario:** Reprograma la frecuencia del `APScheduler` y ejecuta un recálculo masivo del impuesto y márgenes sobre toda la base de datos existente.

---

### 🔐 Autenticación e Integraciones

#### 1. Capturar Sesión de Facebook
- **Método:** `POST /api/auth/facebook`
- **Descripción:** Lanza un proceso hijo de Playwright en modo visible (headed) para que el usuario inicie sesión en Facebook Marketplace. Guarda las cookies activas en `auth.json`.

#### 2. Estado de Sesión de Facebook
- **Método:** `GET /api/auth/facebook/status`

#### 3. Subir Credenciales de Google Sheets
- **Método:** `POST /api/auth/google-sheets/credentials` (Form-data multipart con archivo `file`).

#### 4. Exportar a Google Sheets
- **Método:** `POST /api/export-sheets`
- **Body JSON:**
  ```json
  {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "vehicle_ids": [1, 2, 3]
  }
  ```

---

## 🧮 Motor de Cálculo Financiero (`calculator/financial.py`)

El sistema evalúa cada vehículo según la siguiente formulación matemática de arbitraje:

1. **Impuesto de Transferencia Automotriz ($T$):**
   $$T = P_{\text{estimado}} \times \left(\frac{\text{Tasa \%}}{100}\right)$$
   *(Por defecto Tasa % = 1.5%)*

2. **Costo Total de Adquisición ($C_{\text{total}}$):**
   $$C_{\text{total}} = P_{\text{publicado}} + T + \text{Colchón Mecánico}$$

3. **Margen Neto Estimado ($M$):**
   $$M = P_{\text{estimado}} - C_{\text{total}}$$

4. **Porcentaje de Rentabilidad ($R$):**
   $$R = \left(\frac{M}{P_{\text{estimado}}}\right) \times 100$$

5. **Clasificación del Semáforo:**
   - 🟢 **VERDE:** $R \ge 30\%$
   - 🟡 **AMARILLO:** $15\% \le R < 30\%$
   - 🔴 **ROJO:** $R < 15\%$

---

## 🗄️ Base de Datos y Migraciones Auto-Gestionadas (`database.py`)

El sistema utiliza **SQLite** con conexión única y aislamiento por subproceso.
Para asegurar la evolución sin pérdidas de datos, `database.py` incluye una función de migración en frío `init_db()` que:
1. Crea las tablas relacionales (`vehicles`, `sentinel_configs`, `filter_keywords`) mediante `Base.metadata.create_all()`.
2. Inspecciona las columnas existentes con `PRAGMA table_info(vehicles)`.
3. Aplica sentencias `ALTER TABLE ADD COLUMN` automáticamente cuando se incorporan nuevas métricas (como columnas específicas para Chileautos o Facebook Marketplace).

---

## 🛠️ Scripts Utilitarios

- **`python seed_data.py`:** Inserta oportunidades demostrativas iniciales y palabras clave de descarte por defecto ("prenda", "chocado", "desarme", "panne", "sin padrón").
- **`python clear_db.py`:** Purga todos los registros de la tabla `vehicles`.
- **`python test_chileautos.py`:** Script rápido de prueba para la extracción y parsing de medianas en Chileautos.
